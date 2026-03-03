from pathlib import Path

from mtf.testing.model_data import ModelData
from mtf.testing.nc_model_data import NetcdfModelData
from mtf.testing.text_model_data import TextModelData


def create_model_data(data_file: Path, move: bool = False) -> ModelData:
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
