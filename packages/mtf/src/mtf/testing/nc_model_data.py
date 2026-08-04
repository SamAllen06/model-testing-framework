from collections.abc import Iterator
import os
from pathlib import Path
import tempfile
import shutil
import weakref

from netCDF4 import Dataset
import numpy.typing as npt

from mtf.testing.model_data import ModelData


class NetcdfModelData(ModelData):
    """
    A subclass of ModelData that represents a data file in NetCDF form.
    """

    # Move is likely to be significantly faster than making a copy, as, if moving to the
    # same filesystem, it should just involve changing a file pointer.
    def __init__(self, data_file: Path, move: bool = False):
        self._backing_filepath = self._create_backing_file(data_file, move)
        self._dataset = None

    # Note that if NetcdfModelData is freed, this file will not exist.
    def get_backing_filepath(self) -> Path:
        """
        Gets the absolute location of a given file.
        
        :return: The path to the given file
        :rtype: Path
        """

        return self._backing_filepath
    
    def get_dimensions_for_variable(self, variable: str) -> tuple[str]:
        """
        Gets the dimensions of a given variable using its name.
        
        :param variable: Name of the variable of interest
        :type variable: str
        :return: The dimensions of the variable
        :rtype: tuple[str]
        """
        
        self._assert_dataset_is_open()

        return self._dataset.variables[variable].dimensions

    def __enter__(self) -> None:
        self._dataset = Dataset(self._backing_filepath, "r", format="NETCDF4")

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        self._dataset.close()
        self._dataset = None

    def __getitem__(self, key: str) -> npt.ArrayLike:
        self._assert_dataset_is_open()

        return self._dataset.variables[key][:]

    def __iter__(self) -> Iterator:
        self._assert_dataset_is_open()

        return iter(self._dataset.variables.keys())

    def __len__(self) -> int:
        self._assert_dataset_is_open()

        return len(self._dataset.variables)

    def _create_backing_file(self, data_file: Path, move: bool) -> Path:
        file = tempfile.NamedTemporaryFile(delete=False)
        path = Path(file.name)
        file.close()

        if move:
            shutil.move(data_file, path)
        else:
            shutil.copyfile(data_file, path)

        # Delete the file after this object is garbage collected.
        weakref.finalize(self, os.unlink, path)

        return path

    def _assert_dataset_is_open(self) -> None:
        if self._dataset is None:
            raise OSError(
                "You must open the file backing this ModelData object by using the "
                "context manager interface"
            )
