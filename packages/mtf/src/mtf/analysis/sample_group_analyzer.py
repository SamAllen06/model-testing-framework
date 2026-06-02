from abc import ABC, abstractmethod

from mtf.output.file_utils import FileSystemTree
from mtf.sampling import SampleGroup
from mtf.testing import ModelData


class SampleGroupAnalyzer(ABC):
    @abstractmethod
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        reference_data: ModelData,
        sample_data: list[ModelData],
    ) -> tuple[str, FileSystemTree]:
        pass
