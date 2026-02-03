from abc import ABC, abstractmethod
from pathlib import Path
from typing import Mapping

import netCDF4
import numpy.typing as npt


class ParamEditor(ABC):
    """
    Modifies the values of parameters stored in the model's input parameter file.
    """

    @abstractmethod
    def modify_parameters(self, value_map: Mapping[str, npt.NDArray]) -> None:
        """
        Modifies the values of parameters.
        
        :param value_map: A mapping of parameter names to their new values
        :type value_map: Mapping[str, npt.NDArray]
        """

        pass


class TextParamEditor(ParamEditor):
    """
    Modifies the values of text parameters stored in the model's input parameter file.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def modify_parameters(self, value_map: Mapping[str, npt.NDArray]) -> None:
        """
        Modifies the values of text parameters.
        
        :param value_map: A mapping of parameter names to their new values
        :type value_map: Mapping[str, npt.NDArray]
        """

        with open(self.file_path, "r") as file:
            lines = file.readlines()

        found_map = {parameter: False for parameter in value_map.keys()}

        for index, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line in value_map:
                value = value_map[stripped_line]

                # If not a 0D array (scalar), throw an error.
                if not value.shape == ():
                    raise ValueError(
                        f"Value for {stripped_line} is not a scalar, which is not "
                        "supported in a text parameter file"
                    )

                lines[index + 1] = str(value_map[stripped_line]) + "\n"
                found_map[stripped_line] = True

        for parameter in found_map.keys():
            if not found_map[parameter]:
                raise KeyError(
                    f"Could not find parameter \"{parameter}\" "
                    f"in {self.file_path}."
                )

        with open(self.file_path, "w") as file:
            file.writelines(lines)


class NetCDFParamEditor(ParamEditor):
    """
    Modifies the values of NetCDF parameters stored in the model's input parameter file.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def modify_parameters(self, value_map: Mapping[str, npt.NDArray]) -> None:
        """
        Modifies the values of NetCDF parameters.
        
        :param value_map: A mapping of parameter names to their new values
        :type value_map: Mapping[str, npt.NDArray]
        """

        with netCDF4.Dataset(self.file_path, "r+", format="NETCDF4") as dataset:
            found_map = {parameter: False for parameter in value_map.keys()}

            for name, value in value_map.items():
                if name not in value_map.keys():
                    continue

                dataset.variables[name] = value
                found_map[name] = True
                
            not_found = []
            for name, found in found_map.items():
                if not found:
                    not_found.append(name)

            if not_found:
                raise KeyError(
                    f"Could not find parameters \"{not_found}\" "
                    f"in {self.file_path}."
                )


def make_param_editor(file_path: Path) -> ParamEditor:
    """
    Returns the ParamEditor that corresponds to the given file type.
    
    :param file_path: Path to the file containing parameters
    :type file_path: Path
    :return: A specific ParamEditor subclass
    :rtype: ParamEditor
    """

    extension = file_path.suffix

    match extension:
        case ".txt":
            return TextParamEditor(file_path)
        case ".nc":
            return NetCDFParamEditor(file_path)
        case _:
            raise ValueError(f"'{extension}' is not a supported file type")
