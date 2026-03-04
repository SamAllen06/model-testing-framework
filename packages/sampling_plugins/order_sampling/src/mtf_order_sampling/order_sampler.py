from configparser import ConfigParser
import json
from pathlib import Path
from typing import Mapping

from mtf import root
from mtf.sampling import SampleGroup, Sampler

from mtf_ranges import BoundTranslator, RangeReader
from .order import Order
from .order_factory import OrderFactory


CONFIG_FILE = root.get_config_path(
    root.ConfigPath.SAMPLING_PLUGINS
) / "order_sampling.ini"
APP_ROOT = root.get_app_root()


class OrderSampler(Sampler):
    def __init__(self):
        config_parser = ConfigParser()
        config_parser.read(CONFIG_FILE)
        bound_translator = BoundTranslator(
            RangeReader(APP_ROOT / config_parser["Paths"]["range_path"])
        )
        self._order_factory = OrderFactory(bound_translator)
        self._order_directory = APP_ROOT / config_parser["Paths"]["order_directory"]

    def get_sample_groups(self) -> Mapping[str, SampleGroup]:
        order_paths = list(self._order_directory.glob("*.json"))

        groups = {}

        for path in order_paths:
            order_name = path.name.removesuffix(".json")
            order_data = self._read_order_data(path)

            try:
                order = self._order_factory.construct_order(order_data)
                groups[order_name] = order.to_sample_group()
            except KeyError:
                raise KeyError(f"Invalid order format in order {order_name}")

        return groups

    def _read_order_data(self, order_path: Path) -> Order:
        with open(order_path) as order_file:
            try:
                order_data = json.loads(order_file.read())
            except json.JSONDecodeError as error:
                raise RuntimeError(f"Invalid json in order {str(order_path)}", error)

        return order_data
