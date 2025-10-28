from abc import ABC, abstractmethod
import copy
import logging
from pathlib import Path

import netCDF4


logger = logging.getLogger("testing")


class DefaultsWriter(ABC):
    @abstractmethod
    def write_defaults(self) -> None:
        pass


    @abstractmethod
    def get_defaults(self) -> None:
        pass


class TextDefaultsWriter(DefaultsWriter):
    def __init__(self, defaults_path: Path, param_path: Path):
        self._defaults = self._read_defaults(defaults_path)
        self._param_path = param_path

    def write_defaults(self) -> None:
        lines = []

        for key in self._defaults:
            lines.append(key + "\n")
            value = self._defaults[key]
            lines.append(str(value) + "\n")

        with open(self._param_path, "w") as param_file:
            param_file.writelines(lines)

    def get_defaults(self) -> dict[str, float]:
        return copy.copy(self._defaults)

    def _read_defaults(self, defaults_path: Path) -> dict[str, float]:
        defaults = {}

        with open(defaults_path, "r") as defaults_file:
            lines = defaults_file.readlines()

        keys = [lines[index].strip() for index in range(0, len(lines), 2)]
        values = [float(lines[index]) for index in range(1, len(lines), 2)]

        for key, value in zip(keys, values):
            defaults[key] = value

        return defaults


class NetCDFDefaultsWriter(DefaultsWriter):
    def __init__(self, defaults_path: Path, param_path: Path):
        self._defaults = self._read_defaults(defaults_path)
        self._param_path = param_path

    def write_defaults(self) -> None:
        with netCDF4.Dataset(self._param_path, "r+", format="NETCDF4") as dataset:
            for name, value in self._defaults.items():
                dataset.variables[name][0] = value

    def get_defaults(self) -> dict[str, float]:
        return copy.copy(self._defaults)

    def _read_defaults(self, defaults_path: Path) -> dict[str, float]:
        defaults = {}

        with netCDF4.Dataset(defaults_path, "r", format="NETCDF4") as dataset:
            for name, variable in dataset.variables.items():
                if not variable.shape == tuple():
                    logger.warning(
                        f"Non-scalar inputs are not supported ({name})"
                    )
                    continue

                defaults[name] = variable[0].item()

        return defaults


# Rather than checking extensions, using a file type checker may be better to have in
# the future.
def make_defaults_writer(defaults_path: Path, param_path: Path) -> DefaultsWriter:
    extension = defaults_path.suffix

    if not extension == param_path.suffix:
        raise ValueError(
            "Reading from and writing to seperate file types is not supported"
        )

    match extension:
        case ".txt":
            return TextDefaultsWriter(defaults_path, param_path)
        case ".nc":
            return NetCDFDefaultsWriter(defaults_path, param_path)
        case _:
            raise ValueError(f"'{extension}' is not a supported file type")
