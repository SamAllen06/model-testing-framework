from pathlib import Path
from collections.abc import Mapping, Sequence

from util import Table, TransparentLayerList


class GroupDataStore:
    def __init__(self, reference_data: Mapping[str, Sequence[float]]):
        self._reference_data = reference_data
        self._current_group_data = self._generate_empty_group_data()

    def store_sample_data(self, data: Mapping[str, Sequence[float]]) -> None: 
        current_group_data_sequence = self._current_group_data.as_sequence()

        # Handles the case where a variable doesn't generate data in the test data but
        # does in the reference.
        if not current_group_data_sequence[0].keys() == data.keys():
            # Handle this using an event or something later.
            missing_keys = current_group_data_sequence[0].keys() - data.keys()
            print(f"Test data missing keys: {missing_keys}")

            for key in missing_keys:
                data[key] = [float("nan")]

        current_group_data_sequence.append(data)

    def pop_group_data(self) -> Table[dict, TransparentLayerList]:
        group_data = self._current_group_data
        self._current_group_data = self._generate_empty_group_data()
        return group_data

    def group_data_exists(self) -> bool:
        return self._current_group_data.get_row_count() > 1

    def _generate_empty_group_data(self) -> Table[dict, TransparentLayerList]:
        data: Table[dict, TransparentLayerList] = Table({}, TransparentLayerList())
        data_sequence = data.as_sequence()
        data_sequence.initialize_keys(self._reference_data.keys())
        data_sequence.append(self._reference_data)
        return data
