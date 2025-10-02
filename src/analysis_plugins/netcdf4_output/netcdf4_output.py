from collections.abc import Mapping, MutableSequence, Sequence
from io import StringIO
from pathlib import Path
import tempfile

from netCDF4 import Dataset
import numpy as np
import numpy.ma as npma

from analysis import SampleGroupAnalyzer
from output.file_utils import FileSystemTree
from sampling import SampleGroup
from util import Table


class NetCDF4Output(SampleGroupAnalyzer):
    def analyze_sample_data(
        self, sample_group: SampleGroup, data: Table
    ) -> tuple[str, FileSystemTree]:
        # Create a temp file for the dataset before it's copied into the right place.
        # Caller is responsible for deletion of this file.
        temp_data_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)

        try:
            with Dataset(temp_data_file.name, "w", format="NETCDF4") as dataset:
                self._create_dataset(dataset, sample_group, data)
        finally:
            temp_data_file.close()

        return (
            "Success",
            FileSystemTree.create_from_temp_file(".nc", Path(temp_data_file.name)),
        )

    def _create_dataset(
        self, dataset: Dataset, sample_group: SampleGroup, data: Table
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

        output_data = {}
        for output, values in data_seq[0].items():
            shape = inputs_shape + (len(values),)
            output_data[output] = npma.empty(shape)
            output_data[output].mask = npma.ones(shape, dtype=bool)

        # A better design would have been to require samples to define a value for each
        # input variable, not just the ones they are actively changing, but I'm not sure
        # I'll have time to fix that, so for now it just relies on the first sample
        # setting a value for all used outputs (which they should).
        for outputs, sample in zip(data_seq, filled_samples):
            sample_indices = self._convert_sample_to_indices(
                sample, input_value_to_index, input_order
            )

            for output, values in outputs.items():
                output_data[output][sample_indices] = values

        for output, values in data_seq[0].items():
            variable = dataset.createVariable(output, "f8", input_order + ("index",))
            variable[:] = output_data[output]

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
        self, dataset: Dataset, input_values: dict[str, list[float]]
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
