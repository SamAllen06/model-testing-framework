import numpy as np

from configparser import ConfigParser

from mtf import root
from mtf.sampling import Sample, Sampler, SampleGroup

from mtf.sampling_libs.ranges import RangeReader
from .csv_indices_group import CsvIndicesGroup

CONFIG_FILE = root.get_config_path(
    root.ConfigPath.SAMPLING_PLUGINS
) / "csv_index_sampling.ini"
APP_ROOT = root.get_app_root()


class CsvIndexSampler(Sampler):
    def __init__(self):
        config = ConfigParser()
        config.read(CONFIG_FILE)

        self.range_reader = RangeReader(APP_ROOT / config["Paths"]["range_path"])
        self.csv_directory = APP_ROOT / config["Paths"]["csv_index_files_directory"]

    def get_sample_groups(self) -> dict[str, SampleGroup]:
        groups: dict[str, SampleGroup] = {}

        for csv_file in self.csv_directory.iterdir():
            if not csv_file.is_file():
                continue

            #groups[csv_file.stem] = CsvIndicesGroup(csv_file, self.range_reader)
            samples = []
            indices_group = CsvIndicesGroup(csv_file, self.range_reader)
            for sample_values in indices_group:
                array_sample_values = {
                    key: np.array(value) for key, value in sample_values.items()
                }
                samples.append(Sample(array_sample_values))

            groups[csv_file.stem] = SampleGroup(samples)

        return groups

