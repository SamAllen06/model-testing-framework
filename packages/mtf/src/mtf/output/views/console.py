from collections.abc import Callable
from sys import stderr

from mtf.output.console_utils import ansi, indentation
from mtf.output.events import Event, event_bus
from mtf.output.views.view import View
from mtf.sampling import Sample


class ConsoleView(View):
    def _get_event_subscriptions(self) -> dict[Event, Callable[..., None]]:
        return {
            Event.LOADING_BINARY: self._on_loading_binary,
            Event.BINARY_LOAD_SUCCESS: self._on_binary_load_success,
            Event.BINARY_LOAD_FAILURE: self._on_binary_load_failure,

            Event.BEGAN_LOADING_SAMPLING_PLUGINS: self._on_began_loading_sampling_plugins,
            Event.LOADING_SAMPLING_PLUGIN: self._on_loading_plugin,
            Event.SAMPLING_PLUGIN_LOAD_SUCCESS: self._on_plugin_load_success,
            Event.SAMPLING_PLUGIN_LOAD_FAILURE: self._on_plugin_load_failure,
            Event.SAMPLING_PLUGINS_LOAD_SUCCESS: self._on_sampling_plugins_load_success,
            Event.SAMPLING_PLUGINS_LOAD_FAILURE: self._on_sampling_plugins_load_failure,

            Event.BEGAN_LOADING_ANALYSIS_PLUGINS: self._on_began_loading_analysis_plugins,
            Event.LOADING_ANALYSIS_PLUGIN: self._on_loading_plugin,
            Event.ANALYSIS_PLUGIN_LOAD_SUCCESS: self._on_plugin_load_success,
            Event.ANALYSIS_PLUGIN_LOAD_FAILURE: self._on_plugin_load_failure,
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
            Event.BEGAN_SAMPLE_ANALYSIS_WITH_PLUGIN: self._on_began_analysis_with_plugin,
            Event.SAMPLE_ANALYSIS_WITH_PLUGIN_SUCCESS: self._on_analysis_with_plugin_success,
            Event.SAMPLE_ANALYSIS_WITH_PLUGIN_FAILURE: self._on_analysis_with_plugin_failure,

            Event.BEGAN_GROUP_ANALYSIS: self._on_began_group_analysis,
            Event.BEGAN_GROUP_ANALYSIS_WITH_PLUGIN: self._on_began_analysis_with_plugin,
            Event.GROUP_ANALYSIS_WITH_PLUGIN_SUCCESS: self._on_analysis_with_plugin_success,
            Event.GROUP_ANALYSIS_WITH_PLUGIN_FAILURE: self._on_analysis_with_plugin_failure,

            Event.TESTING_COMPLETED: self._on_testing_completed,
        }

    def _on_loading_binary(self, binary_name: str) -> None:
        print(f"Loading Binary: {binary_name}...", end="")

    def _on_binary_load_success(self) -> None:
        ansi.reset_line()
        ansi.print_ansi_color("Successfully loaded binary.\n", ansi.AnsiColor.BRIGHT_GREEN)

    def _on_binary_load_failure(self, reason: Exception) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            f"Failed to load binary due to {type(reason).__name__}.",
            ansi.AnsiColor.BRIGHT_RED,
            file=stderr
        )
        ansi.print_ansi_color(str(reason) + "\n", ansi.AnsiColor.BRIGHT_RED, file=stderr)

    def _on_began_loading_sampling_plugins(self) -> None:
        print("Loading sampling plugins:")

    def _on_loading_plugin(self, plugin_name: str) -> None:
        indentation.print_indented(f"[{plugin_name}]: Loading...", 1, end="")

    def _on_plugin_load_success(self, plugin_name: str) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(f"[{plugin_name}]: Loaded", 1),
            ansi.AnsiColor.BRIGHT_GREEN
        )

    def _on_plugin_load_failure(self, plugin_name: str, reason: Exception) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(
                f"[{plugin_name}]: Load Failed ({type(reason).__name__})", 1
            ),
            ansi.AnsiColor.BRIGHT_RED
        )

    def _on_sampling_plugins_load_success(self, count: int) -> None:
        if count == 1:
            string = f"\nLoaded {count} sampling plugin successfully.\n"
        else:
            string = f"\nLoaded {count} sampling plugins successfully.\n"
        print(string)

    def _on_sampling_plugins_load_failure(self) -> None:
        ansi.print_ansi_color(
            "\nAll sampling plugins failed to load, exiting...\n",
            ansi.AnsiColor.BRIGHT_RED,
            file=stderr
        )

    def _on_began_loading_analysis_plugins(self) -> None:
        print("Loading analysis plugins:")

    def _on_analysis_plugins_load_success(self, count: int) -> None:
        if count == 1:
            string = f"\nLoaded {count} analysis plugin successfully.\n"
        else:
            string = f"\nLoaded {count} analysis plugins successfully.\n"
        print(string)


    def _on_analysis_plugins_load_failure(self) -> None:
        ansi.print_ansi_color(
            "\nAll analysis plugins failed to load, exiting...\n",
            ansi.AnsiColor.BRIGHT_RED,
            file=stderr
        )

    def _on_began_sample_generation(self) -> None:
        print("Sampling from plugins:")

    def _on_began_sampling_from_plugin(self, plugin_name: str) -> None:
        indentation.print_indented(f"[{plugin_name}]: Sampling...", 1, end="")

    def _on_sampling_from_plugin_success(
            self,
            plugin_name: str,
            group_sample_counts: dict[str, int]
    ) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(f"[{plugin_name}]:", 1),
            ansi.AnsiColor.BRIGHT_GREEN
        )
        for name in group_sample_counts:
            if group_sample_counts[name] == 1:
                sample_count_string = f"{name}: {group_sample_counts[name]} sample"
            else:
                sample_count_string = f"{name}: {group_sample_counts[name]} samples"
            group_lines = [
                indentation.with_indentation(
                    sample_count_string, 2
                )
            ]
        print("\n".join(group_lines))
        group_count = len(group_sample_counts)
        sample_count = sum(group_sample_counts.values())
        if group_count == 1:
            group_count_string = f"Total: {group_count} group, "
        else:
            group_count_string = f"Total: {group_count} groups, "
        if sample_count == 1:
            sample_count_string = f"{sample_count} sample\n"
        else: 
            sample_count_string = f"{sample_count} samples\n"
        indentation.print_indented(
            group_count_string + sample_count_string, 2
        )

    def _on_sampling_from_plugin_failure(self, plugin_name: str, reason: Exception) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(
                f"[{plugin_name}]: Sampling Failed ({type(reason).__name__})", 1
            ),
            ansi.AnsiColor.BRIGHT_RED
        )

    def _on_sampling_from_plugins_success(self, group_count: int, sample_count: int) -> None:
        if group_count == 1:
            group_count_string = f"Grand Total: {group_count} group, "
        else:
            group_count_string = f"Grand Total: {group_count} groups, "
        if sample_count == 1:
            sample_count_string = f"{sample_count} sample\n"
        else:
            sample_count_string = f"{sample_count} samples\n"
        indentation.print_indented(
            group_count_string + sample_count_string, 1
        )

    def _on_sampling_from_plugins_failure(self) -> None:
        ansi.print_ansi_color("Sampling failed. Exiting...", ansi.AnsiColor.BRIGHT_RED)

    def _on_began_timing_binary(self, binary_name: str) -> None:
        print(f"Timing {binary_name}...", end="")

    def _on_timing_binary_success(self, seconds_estimate: float) -> None:
        formatted_estimate = self._format_estimate(seconds_estimate)
        ansi.reset_line()
        print(f"Time estimated: {formatted_estimate}")
        self._prompt_to_continue_with_testing()

    def _format_estimate(self, seconds_estimate: float) -> str:
        rounded_seconds = round(seconds_estimate)
        days = int(rounded_seconds / 86400)
        rounded_seconds -= days * 86400
        hours = int(rounded_seconds / 3600)
        rounded_seconds -= hours * 3600
        minutes = int(rounded_seconds / 60)
        rounded_seconds -= minutes * 60
        return f"{days}:{hours}:{minutes}:{rounded_seconds}"

    def _on_timing_binary_failure(self, exit_code: int) -> None:
        ansi.print_ansi_color(
            f"Timing estimate failed because binary exited with code {exit_code}",
            ansi.AnsiColor.BRIGHT_RED
        )
        self._prompt_to_continue_with_testing()

    def _prompt_to_continue_with_testing(self) -> None:
        print("Would you like to continue? (Yes/No)")

    def _on_began_sampling_from_group(
            self,
            group_name: str,
            group_index: int,
            group_count: int
    ) -> None:
        print(f"\nGroup {group_index + 1} / {group_count}: {group_name}\n")

    def _on_sample_generated(
            self,
            sample_index: int,
            sample_count: int,
            sample: Sample
    ) -> None:
        print(f"Sample {sample_index + 1} / {sample_count}:")
        for variable, value in sample.get_changed_values().items():
            indentation.print_indented(f"{variable}: {value}", 1)
        print("")

    def _on_running_binary(self, binary_name: str) -> None:
        print(f"Running {binary_name}...", end="")

    def _on_binary_exited(self, exit_code: int) -> None:
        ansi.reset_line()
        if exit_code:
            ansi.print_ansi_color(
                f"Binary exited with code {exit_code}\n", ansi.AnsiColor.BRIGHT_RED
            )
        else:
            ansi.print_ansi_color(
                "Binary ran successfully.\n", ansi.AnsiColor.BRIGHT_GREEN
            )

    def _on_began_sample_analysis(self) -> None:
        print("Sample Analysis:")

    def _on_began_analysis_with_plugin(self, plugin_name: str) -> None:
        indentation.print_indented(f"[{plugin_name}]: Analyzing...", 1, end="")

    def _on_analysis_with_plugin_success(
            self,
            plugin_name: str,
            console_output: str,
    ) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(f"[{plugin_name}]:", 1),
            ansi.AnsiColor.BRIGHT_GREEN
        )
        indentation.print_indented(console_output, 2)
        print("")

    def _on_analysis_with_plugin_failure(
            self,
            plugin_name: str,
            reason: Exception
    ) -> None:
        ansi.reset_line()
        ansi.print_ansi_color(
            indentation.with_indentation(
                f"[{plugin_name}]: Analysis Failed ({type(reason).__name__})\n", 1
            ),
            ansi.AnsiColor.BRIGHT_RED
        )

    def _on_began_group_analysis(self) -> None:
        print("Group Analysis:")

    def _on_testing_completed(self) -> None:
        print("Testing completed.")
