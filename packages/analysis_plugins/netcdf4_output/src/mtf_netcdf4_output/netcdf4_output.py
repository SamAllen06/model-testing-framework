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

import pdb

_CONFIG_PATH = root.get_config_path(
    root.ConfigPath.ANALYSIS_PLUGINS
) / "netcdf4_output.ini"
_CONFIG = ConfigParser()
_CONFIG.read(_CONFIG_PATH)


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
            # pdb.set_trace()
            self._create_dataset(dataset, sample_group, reference_data, sample_data)

        return (
            "Success",
            FileSystemTree.create_from_file(
                ".nc", FileReadType.TEMP_FILE, Path(temp_data_file.name)
            ),
        )
    
    def _create_dataset(
        self,
        dataset: Dataset,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> None:
        input_names = [input for input in sample_group[0].keys()]
        sample_count = len(sample_group)

        dataset.createDimension("sample_index", sample_count)
        # pdb.set_trace()
        for input_name in input_names:
            # Skip constants with non-scalar values for now.
            if sample_group[0][input_name].shape != ():
                continue

            input_var = dataset.createVariable(
                input_name,
                "f8",
                ("sample_index",)
                # compression="zlib",
                # #all the compressors except 'zlib and 'szip' use the HDF5 plugin architecture
                # shuffle=False,
                # #if `True`, the HDF5 shuffle filter is applied to improve zlib compression. Default `True`. Ignored unless `compression = 'zlib'`.
                # complevel=1,
            )
            input_var[:] = [sample[input_name] for sample in sample_group]

        # Create dimensions used by outputs
        # pdb.set_trace()
        with reference_data:
            for output_name, data in reference_data.items():
                dimensions = reference_data.get_dimensions_for_variable(output_name)
                output_shape = data.shape
                for dim_name, dim_length in zip(dimensions, output_shape):
                    if dim_name in dataset.dimensions:
                        continue

                    dataset.createDimension(dim_name, dim_length)

                var_kwargs = dict(compression="zlib", shuffle=True, complevel=3) if dimensions else {}
                dataset.createVariable(
                    output_name,
                    data.dtype,
                    ("sample_index",) + dimensions,
                    **var_kwargs
                    # compression="zlib",
                    # shuffle=True,
                    # complevel=3,
                )
        # pdb.set_trace()
        for sample_index, single_sample_data in enumerate(sample_data):
            with single_sample_data:
                # pdb.set_trace()
                for output_name, output_data in single_sample_data.items():
                    output_var = dataset.variables[output_name]
                    if isinstance(output_data, npma.MaskedArray):
                        fill_value = getattr(
                            output_var, "_FillValue",
                            default_fillvals[output_var.dtype.str[1:]],
                        )
                        output_data = output_data.filled(fill_value)
                    try:
                        output_var[sample_index] = output_data
                    except Exception as e:
                        pdb.set_trace()
                        import sys; sys.path.insert(0, "/tmp")
                        from debug_hdf5_stack import dump_hdf5_error_stack
                        dump_hdf5_error_stack(label)
                        print(f"[PROBE FAIL] {label} -> {type(e).__name__}: {e}")
                        return False