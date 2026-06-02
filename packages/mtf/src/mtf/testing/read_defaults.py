from abc import ABC, abstractmethod
import copy
import logging
from pathlib import Path

import netCDF4
import numpy as np
import numpy.typing as npt


logger = logging.getLogger("testing")


def read_defaults(defaults_path: Path) -> dict[str, npt.NDArray]:
    """
    Gets the defaults from a file. 
    
    :param defaults_path: Path to the file containing defaults
    :type defaults_path: Path
    :return: A dictionary mapping the name of each default type to a NumPy Array of its
    values
    :rtype: dict[str, NDArray]
    """

    match defaults_path.suffix:
        case ".txt":
            return _read_text_defaults(defaults_path)
        case ".nc":
            return _read_netcdf_defaults(defaults_path)
        case _:
            raise ValueError(
                f"Defaults file extension {defaults_path.suffix} is not a supported "
                "format"
            )


def _read_text_defaults(defaults_path: Path) -> dict[str, npt.NDArray]:
    defaults = {}

    with open(defaults_path, "r") as defaults_file:
        lines = defaults_file.readlines()

    keys = [lines[index].strip() for index in range(0, len(lines), 2)]
    values = [float(lines[index]) for index in range(1, len(lines), 2)]

    for key, value in zip(keys, values):
        # Just 0D/scalar arrays for this implementation.
        defaults[key] = np.array(value)

    return defaults


def _read_netcdf_defaults(defaults_path: Path) -> dict[str, npt.NDArray]:
    defaults = {}

    with netCDF4.Dataset(defaults_path, "r", format="NETCDF4") as dataset:
        for name, variable in dataset.variables.items():
            defaults[name] = np.array(variable)

    return defaults
