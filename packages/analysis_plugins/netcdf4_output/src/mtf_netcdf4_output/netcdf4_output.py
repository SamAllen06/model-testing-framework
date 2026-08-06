from collections.abc import Mapping, MutableSequence, Sequence
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
import tempfile

from netCDF4 import Dataset
from netCDF4 import default_fillvals
import numpy as np
import numpy.ma as npma

from mtf import root
from mtf.analysis import SampleGroupAnalyzer
from mtf.output.file_utils import FileReadType, FileSystemTree
from mtf.sampling import Sample, SampleGroup
from mtf.testing import ModelData
from mtf.util import Table

_CONFIG_PATH = root.get_config_path(
    root.ConfigPath.ANALYSIS_PLUGINS
) / "netcdf4_output.ini"
_CONFIG = ConfigParser()
_CONFIG.read(_CONFIG_PATH)

_SAMPLE_INDEX_DIM = "sample_index"

class NetCDF4Output(SampleGroupAnalyzer):
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> tuple[str, FileSystemTree]:

        temp_data_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)
        temp_data_file.close()

        with Dataset(temp_data_file.name, "w", format="NETCDF4") as dataset:
            self._create_dataset(dataset, sample_group, reference_data, sample_data)

        return (
            "Success",
            FileSystemTree.create_from_file(
                ".nc", FileReadType.TEMP_FILE, Path(temp_data_file.name)
            ),
        )

    @staticmethod
    def _resolve_variable_name(dataset: Dataset, name: str, kind: str) -> str:
            # A variable collides with a dimension of the same name
        if name not in dataset.dimensions and name not in dataset.variables:
            return name
        elif _CONFIG["Format"]["rename_colliding_variables"] == "yes":
            # Return a variable name that does not collide with a dimension name.
            candidate = f"{kind}__{name}"
            suffix = 1
            while candidate in dataset.dimensions or candidate in dataset.variables:
                candidate = f"{kind}__{name}__{suffix}"
                suffix += 1
            return candidate
        else:
            # Don't change the variable name. NetCDF4 will internally store it as a 
            # non-coordinate variable to differentiate the variable and dimension
            return name


    def _create_dataset(
        self,
        dataset: Dataset,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> None:
        sample_count = len(sample_group)
        dataset.createDimension(_SAMPLE_INDEX_DIM, sample_count)
        # collect all output metadata, define all dimensions, then define variables to 
        # avoid a situation where a variable has the same name as a dimension but the 
        # variable is defined first, causing an HDF error when the dimension creation is
        # attempted
        with reference_data:
            output_specs: dict[str, tuple[np.dtype, tuple[str, ...]]] = {}
            dimension_lengths: dict[str, int] = {}

            for output_name, data in reference_data.items():
                dimensions = tuple(
                    reference_data.get_dimensions_for_variable(output_name)
                )
                output_specs[output_name] = (data.dtype, dimensions)
                for dim_name, dim_length in zip(dimensions, data.shape):
                    dimension_lengths.setdefault(dim_name, dim_length)

            for dim_name, dim_length in dimension_lengths.items():
                if dim_name in dataset.dimensions:
                    continue
                dataset.createDimension(dim_name, dim_length)
            # Constants: one scalar-per-sample variable per sample-varying constant.
            for constant_name in sample_group[0].keys():
                # Skip constants with non-scalar values for now.
                if sample_group[0][constant_name].shape != ():
                    continue

                var_name = self._resolve_variable_name(dataset, constant_name, "model_constant")
                constant_var = dataset.createVariable(
                    var_name, "f8", (_SAMPLE_INDEX_DIM,)
                )
                if var_name != constant_name:
                    constant_var.original_name = constant_name
                constant_var[:] = [sample[constant_name] for sample in sample_group]
                constant_var.variable_type = "constant"

            # Outputs.
            output_var_names: dict[str, str] = {}
            for output_name, (dtype, dimensions) in output_specs.items():
                var_name = self._resolve_variable_name(dataset, output_name, "model_output")
                output_var_names[output_name] = var_name

                var_kwargs = (
                    dict(compression="zlib", shuffle=True, complevel=3)
                    if dimensions
                    else {}
                )
                output_var = dataset.createVariable(
                    var_name,
                    dtype,
                    (_SAMPLE_INDEX_DIM,) + dimensions,
                    **var_kwargs,
                )
                if var_name != output_name:
                    output_var.original_name = output_name
                output_var.variable_type = "output"

        for sample_index, single_sample_data in enumerate(sample_data):
            with single_sample_data:
                for output_name, output_data in single_sample_data.items():
                    output_var = dataset.variables[output_var_names[output_name]]

                    # Masked scalars can carry a fill value whose dtype does not
                    # match the variable's, which netCDF4 rejects on assignment.
                    if isinstance(output_data, npma.MaskedArray):
                        fill_value = getattr(
                            output_var,
                            "_FillValue",
                            default_fillvals[output_var.dtype.str[1:]],
                        )
                        output_data = output_data.filled(fill_value)

                    output_var[sample_index] = output_data
