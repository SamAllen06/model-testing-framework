from collections.abc import Mapping, MutableSequence, Sequence
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
import tempfile

from netCDF4 import Dataset
import numpy as np
import numpy.ma as npma

from analysis import SampleGroupAnalyzer
from output.file_utils import FileReadType, FileSystemTree
import root
from sampling import SampleGroup
from testing import ModelData
from util import Table

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
        filled_samples = sample_group.collapse_and_fill_down()

        input_names = [input for input in filled_samples[0].keys()]
        sample_count = len(filled_samples)

        dataset.createDimension("sample_index", sample_count)
       
        for input_name in input_names:
            input_var = dataset.createVariable(
                input_name,
                "f8",
                ("sample_index",),
                compression="zlib",
                shuffle=False,
                complevel=1,
            )
            input_var[:] = [sample[input_name] for sample in filled_samples]

        # Create dimensions used by outputs
        with reference_data:
            for output_name, data in reference_data.items():
                dimensions = reference_data.get_dimensions_for_variable(output_name)
                output_shape = data.shape
                for dim_name, dim_length in zip(dimensions, output_shape):
                    if dim_name in dataset.dimensions:
                        continue

                    dataset.createDimension(dim_name, dim_length)

                dataset.createVariable(
                    output_name,
                    data.dtype,
                    ("sample_index",) + dimensions,
                    compression="zlib",
                    shuffle=True,
                    complevel=3,
                )

        for sample_index, single_sample_data in enumerate(sample_data):
            with single_sample_data:
                for output_name, output_data in single_sample_data.items():
                    output_var = dataset.variables[output_name]
                    output_var[sample_index] = output_data
