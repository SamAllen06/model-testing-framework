from collections.abc import Mapping
from configparser import ConfigParser

from mtf import root
from mtf.analysis import PerSampleAnalyzer
from mtf.output.file_utils import FileSystemTree
from mtf.testing import ModelData

from mtf_diff_store import DifferenceStore

from mtf_differences import output

_CONFIG_PATH = root.get_config_path(
    root.ConfigPath.ANALYSIS_PLUGINS
) / "differences.ini"
_CONFIG = ConfigParser()
_CONFIG.read(_CONFIG_PATH)

DIFFERENCE_KEYS = ["reference", "test", "difference", "index"]


class DifferenceAnalyzer(PerSampleAnalyzer):
    def analyze_sample_data(
        self,
        _sample: Mapping[str, float],
        reference_data: ModelData,
        test_data: ModelData,
    ) -> tuple[str, FileSystemTree]:
        tolerance = float(_CONFIG["Tolerance"]["ref_percent"])
        differences = DifferenceStore(reference_data, test_data, tolerance)

        return output.generate_output(differences)
