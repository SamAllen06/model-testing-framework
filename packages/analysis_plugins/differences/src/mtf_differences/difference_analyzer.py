from collections import namedtuple
from collections.abc import Mapping, Sequence
import math

import numpy as np

from mtf.analysis import PerSampleAnalyzer
from mtf.output.file_utils import FileSystemTree
from mtf.testing import ModelData
from mtf.util import Table

from mtf_diff_store import DifferenceStore

from . import output


DIFFERENCE_KEYS = ["reference", "test", "difference", "index"]


class DifferenceAnalyzer(PerSampleAnalyzer):
    def analyze_sample_data(
        self,
        _sample: Mapping[str, float],
        reference_data: ModelData,
        test_data: ModelData,
    ) -> tuple[str, FileSystemTree]:
        differences = DifferenceStore(reference_data, test_data)

        return output.generate_output(differences)
