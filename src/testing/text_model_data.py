from collections.abc import Iterator
import os
from pathlib import Path
import tempfile
import shutil
import weakref

import numpy.typing as npt

from testing.model_data import ModelData
from testing.text_dataset import TextDataset


class TextModelData(ModelData):
    """
    A subclass of ModelData that represents a data file in text form.
    """

    def __init__(self, data_file: Path, move: bool = False):
        self._backing_filepath = self._create_backing_file(data_file, move)
        self._dataset = TextDataset(self._backing_filepath)
        self._dataset.close()

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

        # Text datasets don't encode dimension information.
        return ("index",)

    def __enter__(self) -> None:
        self._dataset.reopen()

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        self._dataset.close()

    def __getitem__(self, key: str) -> npt.ArrayLike:
        self._assert_dataset_is_open()

        return self._dataset.get_variable(key)

    def __iter__(self) -> Iterator:
        return iter(self._dataset.get_variables())

    def __len__(self) -> int:
        return len(self._dataset.get_variables())

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
        if not self._dataset.is_open():
            raise OSError(
                "You must open the file backing this ModelData object by using the "
                "context manager interface"
            )
