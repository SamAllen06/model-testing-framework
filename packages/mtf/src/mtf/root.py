from configparser import ConfigParser
from enum import auto, Enum
from pathlib import Path


_SRC_PATH = Path(__file__).parent.parent


class ConfigPath(Enum):
    ROOT = auto()
    SAMPLING_PLUGINS = auto()
    ANALYSIS_PLUGINS = auto()
    OUTPUT = auto()
    PLUGIN_WHITELIST = auto()


_initialized = False
_config_root: Path
_app_root: Path


def set_config_root(config_root: Path) -> None:
    global _initialized
    global _config_root
    global _app_root

    _config_root = config_root

    # app_root is configured relative to the parent of the config directory.
    config_parent = config_root.parent
    
    parser = ConfigParser()
    parser.read(config_root / "main.ini")

    _app_root = config_parent / parser["AppPaths"]["app_root"]

    _initialized = True


def get_app_root() -> Path:
    _require_initialization()

    return _app_root


def get_source_root() -> Path:
    return _SRC_PATH


def get_config_path(path_type: ConfigPath) -> Path:
    _require_initialization()

    match path_type:
        case ConfigPath.ROOT:
            return _config_root
        case ConfigPath.SAMPLING_PLUGINS:
            return _config_root / "sampling_plugins"
        case ConfigPath.ANALYSIS_PLUGINS:
            return _config_root / "analysis_plugins"
        case ConfigPath.OUTPUT:
            return _config_root / "output"
        case ConfigPath.PLUGIN_WHITELIST:
            return _config_root / "plugin_whitelist.json"

    raise TypeError("path_type must be a ConfigPath")


def _require_initialization() -> None:
    if not _initialized:
        raise RuntimeError("The config_root hasn't been set yet; cannot get paths")
