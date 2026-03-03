from argparse import ArgumentParser
from pathlib import Path
import sys

from mtf import root
from mtf.output import view_manager
from mtf.output.views import ViewType
from mtf.tester import Tester


# Returns the config directory specified by the user.
def _parse_arguments_and_validate_config() -> Path:
    parser = ArgumentParser(
        description="Facilitates black-box testing on a scientific model",
        epilog="See the markdown documentation for more details"
    )

    parser.add_argument("config_dir", help="path to the config directory")

    args = parser.parse_args()

    config_dir = Path(args.config_dir)

    if not config_dir.is_dir():
        print(f"{config_dir} is not a directory.", file=sys.stderr)
        sys.exit(1)

    # Using absolute instead of resolve to avoid resolving system links. Allows
    # config_dir to be a system link and output files relative to the link, not where it
    # links to. Note that I haven't tested if this works with the rest of the program.
    return config_dir.absolute()


def _enable_requested_views() -> None:
    requested_views = [ViewType.CONSOLE, ViewType.FILE, ViewType.LOGS]
    view_manager.enable_views(requested_views)


def _user_wants_to_continue_testing() -> bool:
    if input().strip().casefold() in ["yes", "y"]:
        return True
    return False


def main():
    config_dir = _parse_arguments_and_validate_config()
    root.set_config_root(config_dir)

    _enable_requested_views()

    tester = Tester()
    tester.prepare_for_testing()
    if _user_wants_to_continue_testing():
        tester.test_model()


if __name__ == "__main__":
    main()
