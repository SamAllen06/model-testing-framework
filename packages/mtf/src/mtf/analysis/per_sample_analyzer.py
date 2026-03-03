from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from mtf.output.file_utils import FileSystemTree
from mtf.sampling import Sample
from mtf.testing import ModelData


class PerSampleAnalyzer(ABC):
    @abstractmethod
    def analyze_sample_data(
        self,
        sample: Sample,
        reference_data: ModelData,
        test_data: ModelData, 
    ) -> tuple[str, FileSystemTree]:
        pass
