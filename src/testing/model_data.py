from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path


# Represents a data file, saved as a temp file. Lazy load data from this by opening the
# file (use the context-manager), and use the interface provided by the returned
# Mapping.
class ModelData(ABC, Mapping):
    @abstractmethod
    def get_backing_filepath(self) -> Path:
        pass

    @abstractmethod
    def get_dimensions_for_variable(self, variable: str) -> tuple[str, ...]:
        pass

    @abstractmethod
    def __enter__(self) -> Mapping:
        pass

    @abstractmethod
    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        pass
