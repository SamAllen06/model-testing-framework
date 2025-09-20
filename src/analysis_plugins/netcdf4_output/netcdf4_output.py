from io import StringIO
from pathlib import Path

from netCDF4 import Dataset

from analysis import SampleGroupAnalyzer
from output.file_utils import FileSystemTree
from sampling import SampleGroup
from util import Table


class NetCDF4Output(SampleGroupAnalyzer):
    def analyze_sample_data(
        self,
        sample_group: SampleGroup,
        data: Table
    ) -> tuple[str, FileSystemTree]:
        return ("success", FileSystemTree.create_from_files({Path("success.txt"): StringIO(":)")}))

