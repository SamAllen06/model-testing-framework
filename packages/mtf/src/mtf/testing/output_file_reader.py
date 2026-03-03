from pathlib import Path
from collections.abc import Sequence

import netCDF4
import numpy.ma

from mtf.testing.model_data import ModelData
from mtf.testing import model_data_factory


class OutputFileReader():
    def __init__(self, reference_file_path: Path, test_file_path: Path):
        self._reference_data = self._read_data(reference_file_path, False)
        self._test_file_path = test_file_path

    def get_reference_data(self) -> ModelData:
        return self._reference_data

    def read_sample_data(self) -> ModelData:
        return self._read_data(self._test_file_path, True)

    def _read_data(self, file_path: Path, move: bool) -> ModelData:
        return model_data_factory.create_model_data(file_path, move)
