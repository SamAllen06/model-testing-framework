from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from output.file_utils import FileSystemTree
from testing import ModelData


class PerSampleAnalyzer(ABC):
    @abstractmethod
    def analyze_sample_data(
        self,
        sample: Mapping[str, float],
        reference_data: ModelData,
        test_data: ModelData, 
    ) -> tuple[str, FileSystemTree]:
        pass
