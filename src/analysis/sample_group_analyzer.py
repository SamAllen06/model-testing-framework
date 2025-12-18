from abc import ABC, abstractmethod

from output.file_utils import FileSystemTree
from sampling import SampleGroup
from testing import ModelData


class SampleGroupAnalyzer(ABC):
    @abstractmethod
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> tuple[str, FileSystemTree]:
        pass
