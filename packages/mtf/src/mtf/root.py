from configparser import ConfigParser
from enum import auto, Enum
from pathlib import Path


_SRC_PATH = Path(__file__).parent.parent


class ConfigPath(Enum):
    """Identifies which ConfigPath to get."""

    ROOT = auto()
    SAMPLING_PLUGINS = auto()
    ANALYSIS_PLUGINS = auto()
    OUTPUT = auto()
    PLUGIN_WHITELIST = auto()


_initialized = False
_config_root: Path
_app_root: Path


def set_config_root(config_root: Path) -> None:
    """
    Sets the path for the configuration directory, which will be used by the rest of the
    program. 
    
    :param config_root: directory that contains all the configuration files used by the 
    testing program's modules
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
    Returns the parent of the configuration directory, which contains all the files 
    created and modified by the project. 
    
    :return: The root of the project
    :rtype: Path
    """

    _require_initialization()

    return _app_root


def get_source_root() -> Path:
    """
    Returns the directory containing the source code of the program.
    
    :return: The root containing the source code of the program
    :rtype: Path
    """

    return _SRC_PATH


def get_config_path(path_type: ConfigPath) -> Path:
    """
    Returns the requested configuration directory. 
    
    :param path_type: The requested configuration directory
    :type path_type: ConfigPath
    :return: The path to the requested configuration directory
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


def _require_initialization() -> None:
    if not _initialized:
        raise RuntimeError("The config_root hasn't been set yet; cannot get paths")
