from pathlib import Path

from testing.model_data import ModelData
from testing.nc_model_data import NetcdfModelData
from testing.text_model_data import TextModelData


def create_model_data(data_file: Path, move: bool = False) -> ModelData:
    """
    Creates the matching model data based on the file's type. 
    
    :param data_file: Path to a file containing data
    :type data_file: Path
    :param move: Whether the file ought to be moved, always False
    :type move: bool
    :return: An instance of the model data class matching the file type
    :rtype: ModelData
    """

    file_extension = data_file.suffix

    match file_extension:
        case ".txt":
            return TextModelData(data_file, move)
        case ".nc":
            return NetcdfModelData(data_file, move)
        case _:
            raise ValueError(
                f"Data files using the extension {file_extension} are currently not "
                "supported"
            )
