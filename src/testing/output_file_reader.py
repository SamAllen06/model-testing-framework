from pathlib import Path
from abc import ABC, abstractmethod
from collections.abc import Sequence

import netCDF4
import numpy.ma


class OutputFileReader(ABC):
    def __init__(self, reference_file_path: Path, test_file_path: Path):
        self._reference_data = self._read_data(reference_file_path)
        self._test_file_path = test_file_path

    def get_reference_data(self) -> dict[str, list[float]]:
        return self._reference_data

    def read_sample_data(self) -> dict[str, list[float]]:
        return self._read_data(self._test_file_path)

    @abstractmethod
    def _read_data(self, file_path: Path) -> dict[str, list[float]]:
        pass


class TextOutputFileReader(OutputFileReader):
    def _read_data(self, file_path: Path) -> dict[str, list[float]]:
        with open(file_path, "r") as file:
            lines = file.readlines()

        data: dict[str, list[float]] = {}

        for line in lines:
            stripped_line = line.strip()
            if "%" in stripped_line:
                parameter_name = stripped_line
                data[parameter_name] = []
                continue

            data[parameter_name] += [
                float(value) for value in stripped_line.split()
            ]

        return data


class NetCDFOutputFileReader(OutputFileReader):
    def _read_data(self, file_path: Path) -> dict[str, Sequence[float]]:
        data = {}

        with netCDF4.Dataset(file_path, "r", format="NETCDF4") as dataset:
            for name, variable in dataset.variables.items():
                # May result in masked values and numpy types, should still work though.
                # Currently keeping it 1D row-major to avoid breaking later code.
                data[name] = variable[:].ravel()

        return data


def make_output_file_reader(
        reference_file_path: Path, test_file_path: Path
) -> OutputFileReader:
    extension = reference_file_path.suffix

    if not extension == test_file_path.suffix:
        raise ValueError(
            "Reading from seperate test and reference file types is not supported"
        )

    match extension:
        case ".txt":
            return TextOutputFileReader(reference_file_path, test_file_path)
        case ".nc":
            return NetCDFOutputFileReader(reference_file_path, test_file_path)
        case _:
            raise ValueError(f"'{extension}' is not a supported file type")
