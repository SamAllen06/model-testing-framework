from collections.abc import Mapping, MutableSequence, Sequence
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
import tempfile

import netCDF4
import numpy as np
import numpy.ma as npma

from analysis import SampleGroupAnalyzer
from output.file_utils import FileSystemTree
import root
from sampling import SampleGroup
from util import Table

_CONFIG_PATH = root.get_config_path(
    root.ConfigPath.ANALYSIS_PLUGINS
) / "netcdf4_output.ini"
_CONFIG = ConfigParser()
_CONFIG.read(_CONFIG_PATH)


class NetCDF4Output(SampleGroupAnalyzer):
    def analyze_sample_data(
        self, sample_group: SampleGroup, data: Table
    ) -> tuple[str, FileSystemTree]:
        # Create a temp file for the dataset before it's copied into the right place.
        # Caller is responsible for deletion of this file.
        temp_data_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)

        try:
            with netCDF4.Dataset(temp_data_file.name, "w", format="NETCDF4") as dataset:
                if _CONFIG["Format"].getboolean("store_as_samples"):
                    self._create_sparse_dataset(dataset, sample_group, data)
                else:
                    self._create_dataset(dataset, sample_group, data)
        finally:
            temp_data_file.close()

        return (
            "Success",
            FileSystemTree.create_from_temp_file(".nc", Path(temp_data_file.name)),
        )

    def _create_dataset(
        self, dataset: netCDF4.Dataset, sample_group: SampleGroup, data: Table
    ) -> None:
        filled_samples = sample_group.collapse_and_fill_down()

        input_values = self._represent_samples_as_axes(sample_group)

        self._create_input_variables(dataset, input_values)

        # Any arbitrary order is fine as long as it's defined.
        input_order = tuple(input_values.keys())

        input_value_to_index: dict[str, dict[float, int]] = (
            self._convert_input_axes_to_value_index_map(input_values)
        )

        inputs_shape = tuple(len(input_values[input]) for input in input_order)

        data_seq = data.as_sequence()

        dataset.createDimension("index", None)

        output_variables = {}
        for output, values in data_seq[0].items():
            index_count = len(values)
            variable = dataset.createVariable(
                output,
                "f8",
                input_order + ("index",),
                compression="zlib",
                shuffle=False,
                complevel=1,
                # There is probably a better way to pick this chunk size, but this has
                # worked best in my limited testing.
                chunksizes=tuple(1 for _ in input_order) + (min(4096, index_count),)
            )
            shape = inputs_shape + (len(values),)

            output_variables[output] = variable
       
        indices_to_outputs = {}
        for outputs, sample in zip(data_seq, filled_samples):
            sample_indices = self._convert_sample_to_indices(
                sample, input_value_to_index, input_order
            )
        
            indices_to_outputs[sample_indices] = outputs

        # Sorting by the sample indices
        write_order = sorted(
            indices_to_outputs.items(), key=lambda key_value: key_value[0]
        )

        for output, variable in output_variables.items():
            for input_indices, output_values in write_order:
                variable[input_indices] = output_values[output]

    # Takes a sample group and represents the inputs as values on an axis insead of
    # sequential changes, then returns that representation.
    def _represent_samples_as_axes(
        self, sample_group: SampleGroup
    ) -> dict[str, list[float]]:
        input_values_set: dict[str, set[float]] = {}
        input_values: dict[str, list[float]] = {}

        for sample in sample_group:
            for key, value in sample.items():
                if key not in input_values:
                    input_values[key] = [value]
                    input_values_set[key] = set([value])
                    continue
                if value in input_values_set[key]:
                    continue

                input_values[key].append(value)
                input_values_set[key].add(value)

        return input_values

    def _create_input_variables(
        self, dataset: netCDF4.Dataset, input_values: dict[str, list[float]]
    ) -> None:
        for input, values in input_values.items():
            dataset.createDimension(input, len(values))
            input_var = dataset.createVariable(input, "f8", (input,))
            input_var[:] = values

    # Map values of inputs to indices for the axis so it is easy to convert from
    # sequential sample form to a point in the input space.
    def _convert_input_axes_to_value_index_map(
        self, input_values: dict[str, list[float]]
    ) -> dict[str, dict[float, int]]:
        input_value_to_index: dict[str, dict[float, int]] = {}

        for input, values in input_values.items():
            input_value_to_index[input] = {}
            for index, value in enumerate(values):
                input_value_to_index[input][value] = index

        return input_value_to_index

    def _convert_sample_to_indices(
        self,
        sample: Mapping[str, float],
        input_value_to_index: dict[str, dict[float, int]],
        input_order: tuple[str],
    ) -> tuple[int]:
        mapped_indices = {
            input: input_value_to_index[input][value] for input, value in sample.items()
        }
        return tuple(mapped_indices[input] for input in input_order)
    
    def _create_sparse_dataset(
        self, dataset: netCDF4.Dataset, sample_group: SampleGroup, data: Table
    ) -> None:
        filled_samples = sample_group.collapse_and_fill_down()

        input_names = [input for input in filled_samples[0].keys()]
        sample_count = len(filled_samples)

        sample_index_dim = dataset.createDimension("sample_index", sample_count)
       
        for input_name in input_names:
            input_var = dataset.createVariable(
                input_name,
                "f8",
                (sample_index_dim,),
                compression="zlib",
                shuffle=False,
                complevel=1
            )
            input_var[:] = [sample[input_name] for sample in filled_samples]

        index_dim = dataset.createDimension("index", None)
       
        data_seq = data.as_sequence()
        data_map = data.as_mapping()
        output_names = [output for output in data_seq[0].keys()]

        for output_name in output_names:
            output_var = dataset.createVariable(
                output_name,
                "f8",
                (sample_index_dim, index_dim),
                compression="zlib",
                shuffle=True,
                complevel=3
            )

            output_var[:] = data_map[output_name][1:]
