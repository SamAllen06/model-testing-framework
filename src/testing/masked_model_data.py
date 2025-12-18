from collections.abc import Iterator
from pathlib import Path

import numpy as np
import numpy.typing as npt

from testing.model_data import ModelData


# Used when data is known to be invalid for a sample, but group analysis plugins still
# need to see the same structure used for the data. Will keep all properties of the
# ModelData it wraps (usually the reference), but all values returned will be masked.
class MaskedModelData(ModelData):
    def __init__(self, wrapped_data: ModelData):
        self._wrapped_data = wrapped_data

    def get_backing_filepath(self) -> Path:
        return None
    
    def get_dimensions_for_variable(self, variable: str) -> tuple[str]:
        return self._wrapped_data.get_dimensions_for_variable(variable)

    def __enter__(self) -> None:
        self._wrapped_data.__enter__()

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        self._wrapped_data.__exit__(None, None, None)

    def __getitem__(self, key: str) -> npt.ArrayLike:
        data = self._wrapped_data[key]

        # Returns a view to the original data (no copy), with all elements masked.
        masked_data = np.ma.masked_array(data.data, mask=True, copy=False)
        return masked_data

    def __iter__(self) -> Iterator:
        return self._wrapped_data.__iter__()

    def __len__(self) -> int:
        return len(self._wrapped_data)
