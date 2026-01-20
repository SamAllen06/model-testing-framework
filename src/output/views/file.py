from collections.abc import Callable
from configparser import ConfigParser
import csv
from pathlib import Path
import shutil

from output.events import Event
from output.file_utils import FileSystemTree
from output.views.view import View
import root
from sampling import Sample


class FileView(View):
    _BINARY_EXIT_FILE_HEADERS = ("sample_index", "exit_code")

    def __init__(self) -> None:
        self._read_config()

        self._parameter_order: list[str] = []

        self._current_group: str
        self._current_sample: int


    def _read_config(self) -> None:
        config_path = root.get_config_path(root.ConfigPath.OUTPUT) / "files.ini"

        config = ConfigParser()
        config.read(config_path)

        output_root = root.get_app_root()

        self._samples_directory = output_root / config["Directories"]["samples"]
        self._errors_directory = output_root / config["Directories"]["errors"]
        self._sample_analysis_directory = (
                output_root / config["Directories"]["analysis"] / "sample"
        )
        self._group_analysis_directory = (
                output_root / config["Directories"]["analysis"] / "group"
        )



    def _get_event_subscriptions(self) -> dict[Event, Callable[..., None]]:
        return {
            Event.INITIALIZE: self._on_initialize,
            Event.BEGAN_SAMPLING_FROM_GROUP: self._on_began_sampling_from_group,
            Event.SAMPLE_GENERATED: self._on_sample_generated,
            Event.BINARY_EXITED: self._on_binary_exited,
            Event.SAMPLE_ANALYSIS_WITH_PLUGIN_SUCCESS:
                self._on_sample_analysis_with_plugin_success,
            Event.GROUP_ANALYSIS_WITH_PLUGIN_SUCCESS:
                self._on_group_analysis_with_plugin_success,
        }

    def _prepare_directory(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        for child in directory.iterdir():
            if child.is_file():
                child.unlink()
            else:
                shutil.rmtree(child)

    def _on_initialize(self) -> None:
        directories = [
            self._samples_directory,
            self._errors_directory,
            self._sample_analysis_directory,
            self._group_analysis_directory,
        ]

        for directory in directories:
            self._prepare_directory(directory)

    def _on_began_sampling_from_group(
            self,
            group_name: str,
            group_index: int,
            group_count: int
    ) -> None:
        self._current_group = group_name

    def _on_sample_generated(
            self,
            sample_index: int,
            sample_count: int,
            sample: Sample
    ) -> None:
        self._current_sample = sample_index

        if not self._parameter_order:
            self._parameter_order = list(values.keys())

        sample_group_file = self._samples_directory / f"{self._current_group}.csv"
        is_first_write = not sample_group_file.exists()

        with open(sample_group_file, "a", newline="") as file:
            writer = csv.writer(file)
            
            if is_first_write:
                writer.writerow(self._parameter_order)

            sample_row = [values[parameter] for parameter in self._parameter_order]
            writer.writerow(sample_row)

    def _on_binary_exited(self, exit_code: int) -> None:
        if not exit_code:
            return
        
        error_file = self._errors_directory / f"{self._current_group}.csv"
        is_first_write = not error_file.exists()
        
        with open(error_file, "a", newline="") as file:
            writer = csv.writer(file)

            if is_first_write:
                writer.writerow(self._BINARY_EXIT_FILE_HEADERS)

            writer.writerow((self._current_sample, exit_code))

    def _on_sample_analysis_with_plugin_success(
            self,
            plugin_name: str,
            file_output: FileSystemTree
    ) -> None:
        analysis_tree_parent = self._sample_analysis_directory / self._current_group / plugin_name

        analysis_tree_parent.mkdir(exist_ok=True, parents=True)

        file_output.write_to_filesystem(analysis_tree_parent, str(self._current_sample))

    def _on_group_analysis_with_plugin_success(
            self,
            plugin_name: str,
            file_output: FileSystemTree
    ) -> None:
        analysis_tree_parent = self._group_analysis_directory / self._current_group

        analysis_tree_parent.mkdir(exist_ok=True)

        file_output.write_to_filesystem(analysis_tree_parent, str(plugin_name))
