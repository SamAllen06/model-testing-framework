from collections.abc import Callable
import configparser
import datetime
import logging
import os.path
from pathlib import Path
import traceback
from output.events import Event
from output.views.view import View
import root


class LogsView(View):
    _LATEST_PREFIX = "latest-"
    _LOGGER = logging.getLogger("event")

    def _get_event_subscriptions(self) -> dict[Event, Callable[..., None]]:
        return {
            Event.INITIALIZE: self._on_initialize,
            Event.LOADING_BINARY: self._on_loading_binary,
            Event.BINARY_LOAD_SUCCESS: self._on_binary_load_success,
            Event.BINARY_LOAD_FAILURE: self._on_binary_load_failure,
            Event.BEGAN_LOADING_SAMPLING_PLUGINS: self._on_began_loading_sampling_plugins,
            Event.LOADING_SAMPLING_PLUGIN: self._on_loading_sampling_plugin,
            Event.SAMPLING_PLUGIN_LOAD_SUCCESS: self._on_sampling_plugin_load_success,
            Event.SAMPLING_PLUGIN_LOAD_FAILURE: self._on_sampling_plugin_load_failure,
            Event.SAMPLING_PLUGINS_LOAD_SUCCESS: self._on_sampling_plugins_load_success,
            Event.SAMPLING_PLUGINS_LOAD_FAILURE: self._on_sampling_plugins_load_failure,
            Event.BEGAN_LOADING_ANALYSIS_PLUGINS: self._on_began_loading_analysis_plugins,
            Event.LOADING_ANALYSIS_PLUGIN: self._on_loading_analysis_plugin,
            Event.ANALYSIS_PLUGIN_LOAD_SUCCESS: self._on_analysis_plugin_load_success,
            Event.ANALYSIS_PLUGIN_LOAD_FAILURE: self._on_analysis_plugin_load_failure,
            Event.ANALYSIS_PLUGINS_LOAD_SUCCESS: self._on_analysis_plugins_load_success,
            Event.ANALYSIS_PLUGINS_LOAD_FAILURE: self._on_analysis_plugins_load_failure,
            Event.BEGAN_SAMPLE_GENERATION: self._on_began_sample_generation,
            Event.BEGAN_SAMPLING_FROM_PLUGIN: self._on_began_sampling_from_plugin,
            Event.SAMPLING_FROM_PLUGIN_SUCCESS: self._on_sampling_from_plugin_success,
            Event.SAMPLING_FROM_PLUGIN_FAILURE: self._on_sampling_from_plugin_failure,
            Event.SAMPLING_FROM_PLUGINS_SUCCESS: self._on_sampling_from_plugins_success,
            Event.SAMPLING_FROM_PLUGINS_FAILURE: self._on_sampling_from_plugins_failure,
            Event.BEGAN_TIMING_BINARY: self._on_began_timing_binary,
            Event.TIMING_BINARY_SUCCESS: self._on_timing_binary_success,
            Event.TIMING_BINARY_FAILURE: self._on_timing_binary_failure,
            Event.BEGAN_SAMPLING_FROM_GROUP: self._on_began_sampling_from_group,
            Event.SAMPLE_GENERATED: self._on_sample_generated,
            Event.RUNNING_BINARY: self._on_running_binary,
            Event.BINARY_EXITED: self._on_binary_exited,
            Event.BEGAN_SAMPLE_ANALYSIS: self._on_began_sample_analysis,
            Event.BEGAN_SAMPLE_ANALYSIS_WITH_PLUGIN: self._on_began_sample_analysis_with_plugin,
            Event.SAMPLE_ANALYSIS_WITH_PLUGIN_SUCCESS: self._on_sample_analysis_with_plugin_success,
            Event.SAMPLE_ANALYSIS_WITH_PLUGIN_FAILURE: self._on_sample_analysis_with_plugin_failure,
            Event.BEGAN_GROUP_ANALYSIS: self._on_began_group_analysis,
            Event.BEGAN_GROUP_ANALYSIS_WITH_PLUGIN: self._on_began_group_analysis_with_plugin,
            Event.GROUP_ANALYSIS_WITH_PLUGIN_SUCCESS: self._on_group_analysis_with_plugin_success,
            Event.GROUP_ANALYSIS_WITH_PLUGIN_FAILURE: self._on_group_analysis_with_plugin_failure,
            Event.TESTING_COMPLETED: self._on_testing_completed,
        }

    def _clean_logs(self, log_directory: Path, keep_logs: int) -> None:
        creation_times: dict[float, Path] = {}
        for log in log_directory.iterdir():
            creation_times[os.path.getctime(log)] = log
        if len(creation_times) <= keep_logs:
            return
        sorted_times = list(creation_times.keys())
        sorted_times.sort()
        delete_count = len(creation_times) - keep_logs
        for time_index in range(delete_count):
            time = sorted_times[time_index]
            creation_times[time].unlink()

    def _rename_last_log(self, log_directory: Path) -> None:
        for log in log_directory.iterdir():
            if log.name.startswith(self._LATEST_PREFIX):
                last_log = log
                break
        else:
            return
        new_path = last_log.parent / last_log.name[len(self._LATEST_PREFIX):]
        last_log.rename(new_path)

    def _define_log_file(self) -> None:
        config_path = root.get_config_path(root.ConfigPath.OUTPUT) / "logs.ini"
        config = configparser.ConfigParser()
        config.read(config_path)
        log_directory = root.get_app_root() / config["Directories"]["log_directory"]
        log_directory.mkdir(parents=True, exist_ok=True)
        self._rename_last_log(log_directory)
        
        keep_logs = int(config["Settings"]["keep_logs"])
        if keep_logs > 0:
            self._clean_logs(log_directory, keep_logs - 1)
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
        log_path = log_directory / f"{self._LATEST_PREFIX}{timestamp}.log"
        logging.basicConfig(filename=log_path, level=logging.INFO)

    def _on_initialize(self) -> None:
        self._define_log_file()
        self._LOGGER.info("Initialized")

    def _on_loading_binary(self, binary_name: str) -> None:
        self._LOGGER.info(f'Attemping to find the binary "{binary_name}"...')

    def _on_binary_load_success(self) -> None:
        self._LOGGER.info("Successfully found the binary")

    def _on_binary_load_failure(self, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.critical(f"Failed to find the binary.\n{''.join(formatted_exception)}")

    def _on_began_loading_sampling_plugins(self) -> None:
        self._LOGGER.info("Started loading sampling plugins")

    def _on_loading_sampling_plugin(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Loading sampling plugin "{plugin_name}"')

    def _on_sampling_plugin_load_success(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Successfully loaded sampling plugin "{plugin_name}"')

    def _on_sampling_plugin_load_failure(self, plugin_name: str, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.error(
            f"Failed to load sampling plugin \"{plugin_name}\"\n"
            f"{''.join(formatted_exception)}"
        )

    def _on_sampling_plugins_load_success(self, count: int) -> None:
        self._LOGGER.info(f"Successfully loaded {count} sampling plugins")

    def _on_sampling_plugins_load_failure(self) -> None:
        self._LOGGER.critical(f"No sampling plugins were able to load.")

    def _on_began_loading_analysis_plugins(self) -> None:
        self._LOGGER.info("Started loading analysis plugins")

    def _on_loading_analysis_plugin(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Loading analysis plugin "{plugin_name}"')

    def _on_analysis_plugin_load_success(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Successfully loaded analysis plugin "{plugin_name}"')

    def _on_analysis_plugin_load_failure(self, plugin_name: str, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.error(
            f"Failed to load analysis plugin \"{plugin_name}\"\n"
            f"{''.join(formatted_exception)}"
        )

    def _on_analysis_plugins_load_success(self, count: int) -> None:
        self._LOGGER.info(f"Successfully loaded {count} analysis plugins")

    def _on_analysis_plugins_load_failure(self) -> None:
        self._LOGGER.critical(f"No analysis plugins were able to load")

    def _on_began_sample_generation(self) -> None:
        self._LOGGER.info("Began sample group generation")

    def _on_began_sampling_from_plugin(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Getting sample groups from plugin "{plugin_name}"')

    def _on_sampling_from_plugin_success(self, plugin_name: str, group_sample_counts: dict[str, int]) -> None:
        group_count = len(group_sample_counts)
        sample_count = sum([group_sample_counts[group] for group in group_sample_counts])
        self._LOGGER.info(
            f'Got {group_count} groups with {sample_count} total samples from plugin '
            f'"{plugin_name}"'
        )

    def _on_sampling_from_plugin_failure(self, plugin_name: str, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.error(
            f"Failed to get sample groups from plugin \"{plugin_name}\"\n"
            f"{''.join(formatted_exception)}"
        )

    def _on_sampling_from_plugins_success(self, group_count: int, sample_count: int) -> None:
        self._LOGGER.info(f"Got {group_count} total groups and {sample_count} from plugins")

    def _on_sampling_from_plugins_failure(self) -> None:
        self._LOGGER.critical(f"Failed to get any sample groups from plugins")

    def _on_began_timing_binary(self, binary_name: str) -> None:
        self._LOGGER.info(f"Timing {binary_name}")

    def _on_timing_binary_success(self, seconds_estimate: float) -> None:
        self._LOGGER.info(f"Estimated testing to take {seconds_estimate} seconds")

    def _on_timing_binary_failure(self, exit_code: int) -> None:
        self._LOGGER.warning(
            f"Binary exited with code {exit_code} when using its default inputs, "
            "this may indicate that the testing program is misconfigured"
        )

    def _on_began_sampling_from_group(self, group_name: str, group_index: int, group_count: int) -> None:
        self._LOGGER.info(
            f'Started sampling from group "{group_name}" '
            f'({group_index + 1} / {group_count})'
        )

    def _on_sample_generated(self, sample_index: int, sample_count: int) -> None:
        self._LOGGER.info(f"Generated sample {sample_index + 1} out of {sample_count}")

    def _on_running_binary(self, binary_name: str) -> None:
        self._LOGGER.info(f"Running {binary_name}")

    def _on_binary_exited(self, exit_code: int) -> None:
        if exit_code:
            self._LOGGER.info(f"Binary exited with error code {exit_code}")
        else:
            self._LOGGER.info("Binary exited ok")

    def _on_began_sample_analysis(self) -> None:
        self._LOGGER.info("Began analysis on individual samples")

    def _on_began_sample_analysis_with_plugin(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Began analyzing sample with plugin "{plugin_name}"')

    def _on_sample_analysis_with_plugin_success(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Successfully analyzed sample with plugin "{plugin_name}"')

    def _on_sample_analysis_with_plugin_failure(self, plugin_name: str, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.info(
            f"Failed to analyze sample with plugin \"{plugin_name}\"\n{''.join(formatted_exception)}"
        )

    def _on_began_group_analysis(self) -> None:
        self._LOGGER.info("Began analysis on the sample group as a whole")

    def _on_began_group_analysis_with_plugin(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Began analyzing group with plugin "{plugin_name}"')

    def _on_group_analysis_with_plugin_success(self, plugin_name: str) -> None:
        self._LOGGER.info(f'Successfully analyzed group with plugin "{plugin_name}"')

    def _on_group_analysis_with_plugin_failure(self, plugin_name: str, reason: Exception) -> None:
        formatted_exception = traceback.format_exception(reason)
        self._LOGGER.info(
            f"Failed to analyze group with plugin \"{plugin_name}\"\n{''.join(formatted_exception)}"
        )

    def _on_testing_completed(self) -> None:
        self._LOGGER.info("Finished testing")
