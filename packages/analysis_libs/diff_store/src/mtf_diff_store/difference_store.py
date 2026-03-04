from collections import namedtuple
from collections.abc import Mapping, Iterator

import numpy as np

from mtf.testing import ModelData


VariableDifferences = namedtuple(
    "VariableDifferences", ["indices", "ref", "test", "diff"]
)


class DifferenceStore(Mapping):
    def __init__(self, reference: ModelData, test: ModelData):
        self._differences = {}
        self._unchanged = []
        self._dimensions = {}
        with reference, test:
            self._find_differences(reference, test)

    def get_unchanged_variables(self) -> list[str]:
        return self._unchanged

    def get_variable_dimensions(self, variable: str) -> tuple[str, ...]:
        return self._dimensions[variable]

    def __getitem__(self, variable: str) -> VariableDifferences:
        return self._differences[variable]

    def __iter__(self) -> Iterator:
        return iter(self._differences.keys())

    def __len__(self) -> int:
        return len(self._differences)

    def _find_differences(self, reference: ModelData, test: ModelData) -> None:
        for var in reference.keys():
            ref_data = reference[var]
            test_data = test[var]
            self._dimensions[var] = reference.get_dimensions_for_variable(var)

            # If the data is scalar, put it in a 1D array.
            if ref_data.shape == ():
                ref_data = np.array([ref_data])
                test_data = np.array([test_data])

            total_diff = test_data - ref_data
            indices = np.nonzero(total_diff)

            ref_values = ref_data[indices]
            test_values = test_data[indices]
            diffs = total_diff[indices]

            if len(ref_values) == 0:
                self._unchanged.append(var)
                continue

            self._differences[var] = VariableDifferences(
                np.column_stack(indices),
                ref_values,
                test_values,
                diffs,
            )
