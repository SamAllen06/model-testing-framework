from collections.abc import Mapping, MutableSequence, Sequence
from io import StringIO
from pathlib import Path
import tempfile

from netCDF4 import Dataset
import numpy as np

from analysis import SampleGroupAnalyzer
from output.file_utils import FileSystemTree
from sampling import SampleGroup
from util import Table


class NetCDF4Output(SampleGroupAnalyzer):
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        data: Table
    ) -> tuple[str, FileSystemTree]:
        temp_data_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)
      
        try:
            with Dataset(temp_data_file.name, "w", format="NETCDF4") as dataset:
                self._create_dataset(dataset, sample_group, data)
        finally:
            temp_data_file.close()

        return ("Success",
            #f"Recorded {sample_count} {sample_dimension}-dimensional samples with "
            #f"{output_dimension}-dimensional outputs.",
            FileSystemTree.create_from_temp_file(".nc", Path(temp_data_file.name))
        )

    def _create_dataset(
        self,
        dataset: Dataset,
        sample_group: SampleGroup,
        data: Table
    ) -> None:
        filled_samples = sample_group.collapse_and_fill_down()

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

        input_sizes: dict[str, int] = {}

        for input, values in input_values.items():
            value_count = len(values)
            dataset.createDimension(input, value_count)
            input_var = dataset.createVariable(input, "f8", (input,))
            input_var[:] = values

            input_sizes[input] = value_count

        data_seq = data.as_sequence()

        dataset.createDimension("index", None)

        # Any arbitrary order is fine as long as we know what it is.
        input_order = tuple(input_values.keys())
        shape = tuple([input_sizes[input] for input in input_order])

        # Mapping values to indicies so we can iterate through samples with the output
        # data and quickly convert input values to indicies to store outputs.
        input_value_to_index: dict[str, dict[float, int]] = {}
        for input, values in input_values.items():
            input_value_to_index[input] = {}
            for index, value in enumerate(values):
                input_value_to_index[input][value] = index

        output_variables = {}
        for output, values in data_seq[0].items():
            output_variables[output] = dataset.createVariable(
                output,
                "f8",
                input_order + ("index",)
            )

        for outputs, sample in zip(data_seq, filled_samples):
            sample_indices = self._convert_sample_to_indices(
                sample, input_value_to_index, input_order
            )

            output_data = np.array(outputs[output], dtype="float16")
            output_variables[output][sample_indices + (slice(0, len(outputs[output])),)] = output_data 
        import pdb; pdb.set_trace()
            

    def _convert_sample_to_indices(
        self,
        sample: Mapping[str, float],
        input_value_to_index: dict[str, dict[float, int]],
        input_order: tuple[str]
    ) -> tuple[int]:
        mapped_indices = {
            input: input_value_to_index[input][value] for input, value in sample.items()
        }
        return tuple(mapped_indices[input] for input in input_order)
