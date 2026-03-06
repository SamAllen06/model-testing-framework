from configparser import ConfigParser
from typing import Mapping

from mtf import root
from mtf.sampling import Sampler, SampleGroup

from mtf_netcdf_cases.netcdf_sample_group import NetcdfSampleGroup


class NetcdfSampler(Sampler):
    def __init__(self):
        config_parser = ConfigParser()
        config_path = root.get_config_path(
            root.ConfigPath.SAMPLING_PLUGINS
        ) / "netcdf_cases.ini"
        config_parser.read(config_path)

        self._group_directory = (
                root.get_app_root() / config_parser["Paths"]["group_directory"]
        )

    def get_sample_groups(self) -> Mapping[str, SampleGroup]:
        sample_group_paths = list(self._group_directory.glob("**/*.nc"))

        groups = {}
        for sample_group_path in sample_group_paths:
            name = sample_group_path.stem
            # Will lazy load sample data.
            groups[name] = NetcdfSampleGroup(sample_group_path)

        return groups

                
