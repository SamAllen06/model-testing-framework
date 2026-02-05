from collections import namedtuple
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import numpy.typing as npt

from testing.model_data import ModelData


MetaEntry = namedtuple("MetaEntry", ["shape", "dtype", "dimensions"])


# Used when data is known to be invalid for a sample, but group analysis plugins still
# need to see the same structure used for the data. Will keep all properties of the
# ModelData it wraps (usually the reference), but all values returned will be masked.
class MaskedModelData(ModelData):
    """
    A subclass of ModelData that represents a data file with masked values for invalid
    data from a sample so that group analysis plugins can still see the same structure
    used for the data.
    """

    def __init__(self, wrapped_data: ModelData):
        self._variable_metadata = self._read_metadata(wrapped_data)

    def get_backing_filepath(self) -> Path:
        """
        Gets the absolute location of a given file.
        
        :return: The path to the given file
        :rtype: Path
        """

        return None
    
    def get_dimensions_for_variable(self, variable: str) -> tuple[str]:
        """
        Gets the dimensions of a given variable using its name.
        
        :param variable: Name of the variable of interest
        :type variable: str
        :return: The dimensions of the variable
        :rtype: tuple[str]
        """

        return self._variable_metadata[variable].dimensions

    def __enter__(self) -> None:
        pass

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        pass

    # Returns a snapshot of the original data, with all elements masked. Should be quick
    # to allocate since values aren't initialized, but may cause memory useage issues if
    # too many/too large arrays are used in the future.
    def __getitem__(self, key: str) -> npt.ArrayLike:
        shape = self._variable_metadata[key].shape
        dtype = self._variable_metadata[key].dtype
        return np.ma.masked_array(np.empty(shape, dtype=dtype), mask=True)

    def __iter__(self) -> Iterator:
        return iter(self._variable_metadata)

    def __len__(self) -> int:
        return len(self._variable_metadata)

    def _read_metadata(self, wrapped_data: ModelData) -> dict[str, MetaEntry]:
        result = {}

        with wrapped_data:
            for variable, data in wrapped_data.items():
                shape = data.shape
                dtype = data.dtype
                dimensions = wrapped_data.get_dimensions_for_variable(variable)

                result[variable] = MetaEntry(shape, dtype, dimensions)

        return result

