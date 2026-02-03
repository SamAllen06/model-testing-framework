from pathlib import Path
from collections.abc import Sequence

import netCDF4
import numpy.ma

from testing.model_data import ModelData
from testing import model_data_factory


class OutputFileReader():
    """
    Reads in output data from the model and packages it into a form usable by analysis
    plugins.
    """

    def __init__(self, reference_file_path: Path, test_file_path: Path):
        self._reference_data = self._read_data(reference_file_path, False)
        self._test_file_path = test_file_path

    def get_reference_data(self) -> ModelData:
        """
        Gets reference data from a model.

        Reference data is the data produced by the model when it is run using the
        default parameters. It is meant to be a baseline for comparing sample output.
        
        :return: Reference data from a model
        :rtype: ModelData
        """

        return self._reference_data

    def read_sample_data(self) -> ModelData:
        """
        Reads sample test data from a model.

        Sample test data is the data produced by a model after it has run using a modified
        parameters file. It has the same format as reference data but is read every time
        the function is called.
        
        :return: Sample test data from a model
        :rtype: ModelData
        """

        return self._read_data(self._test_file_path, True)

    def _read_data(self, file_path: Path, move: bool) -> ModelData:
        return model_data_factory.create_model_data(file_path, move)
