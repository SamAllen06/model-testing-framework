from configparser import ConfigParser
from enum import auto, Enum
from pathlib import Path


_SRC_PATH = Path(__file__).parent


class ConfigPath(Enum):
    """Define enumeration to later differentiate config paths."""
    ROOT = auto()
    SAMPLING_PLUGINS = auto()
    ANALYSIS_PLUGINS = auto()
    OUTPUT = auto()
    PLUGIN_WHITELIST = auto()


class PluginPath(Enum):
    """Define enumeration to later differentiate plugin root."""
    SAMPLING_PLUGINS = auto()
    ANALYSIS_PLUGINS = auto()


_initialized = False
_config_root: Path
_app_root: Path


def set_config_root(config_root: Path) -> None:
    """
    Define _app_root relative to the parent of the config directory, set initialized.
    
    :param config_root: directory that contains all the configuration files used by the testing program's modules
    :type config_root: Path
    """
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
    """
    Ensure _app_root has been initialized and return _app_root as a Path.
    
    :return: The root of the project
    :rtype: Path
    """
    _require_initialization()

    return _app_root


def get_source_root() -> Path:
    """
    Return the path to the Source Root
    
    :return: The root containing the source code of the program
    :rtype: Path
    """
    return _SRC_PATH


def get_config_path(path_type: ConfigPath) -> Path:
    """
    Compares a path type to the ConfigPath enumeration and return the matching enum member
    
    :param path_type: A given path type
    :type path_type: ConfigPath
    :return: The ConfigPath enum member path_type matches
    :rtype: Path
    """
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


def get_plugin_root(path_type: PluginPath) -> Path:
    """
    Compares a path type to the PluginPath enumeration and return the matching enum member
    
    :param path_type: A given path type
    :type path_type: PluginPath
    :return: The PluginPath enum member path_type matches
    :rtype: Path
    """
    match path_type:
        case PluginPath.SAMPLING_PLUGINS:
            return _SRC_PATH / "sampling_plugins"
        case ConfigPath.ANALYSIS_PLUGINS:
            return _SRC_PATH / "analysis_plugins"

    raise TypeError("path_type must be a PluginPath")


def _require_initialization() -> None:
    """Check for if config_root is initialized"""
    if not _initialized:
        raise RuntimeError("The config_root hasn't been set yet; cannot get paths")


#CONFIG_ROOT = APP_ROOT / "config"
#SOURCE_ROOT = APP_ROOT / "src" # Replace with plugin root

#SAMPLING_PLUGIN_CONFIG_DIRECTORY = CONFIG_ROOT / "sampling_plugins"
#ANALYSIS_PLUGIN_CONFIG_DIRECTORY = CONFIG_ROOT / "analysis_plugins"
#OUTPUT_CONFIG_DIRECTORY = CONFIG_ROOT / "output"
