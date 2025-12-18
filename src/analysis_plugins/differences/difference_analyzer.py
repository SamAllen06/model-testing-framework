from collections import namedtuple
from collections.abc import Mapping, Sequence
import math

import numpy as np

from analysis import PerSampleAnalyzer
from output.file_utils import FileSystemTree
from testing import ModelData
from util import Table

from . import output
from .difference_store import DifferenceStore


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
