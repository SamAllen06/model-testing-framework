from collections.abc import Mapping
from configparser import ConfigParser
from pathlib import Path
import sys
import time

from output.events import Event, event_bus
from plugin_loading import AnalyzerLoader, SamplerLoader
import root
from sampling import Sample, SampleGroup
from testing import BinaryRunner, MaskedModelData, OutputFileReader, ParamEditor
import testing


class Tester:
    """
    Ties together the entirety of the testing program. Allows the user to verify that 
    the plugins they need have been loaded and that the time estimated for testing is
    reasonable. If so, it runs the tests. 
    """

    def __init__(self) -> None:
        config_path = root.get_config_path(root.ConfigPath.ROOT) / "main.ini"
        app_root = root.get_app_root()

        config = ConfigParser()
        config.read(config_path)

        self._binary_runner = testing.BinaryRunner()
        
        self._sampler_loader = SamplerLoader()
        self._analyzer_loader = AnalyzerLoader()

        self._defaults = testing.read_defaults(
            app_root / config["Model"]["parameter_defaults"]
        )
        Sample.set_defaults(self._defaults)

        self._param_editor = testing.make_param_editor(
            app_root / config["Model"]["parameters"]
        )
        self._output_file_reader = OutputFileReader(
            app_root / config["Model"]["reference_output"],
            app_root / config["Model"]["test_output"],
        )
        self._reference_data = self._output_file_reader.get_reference_data()
        self._group_data = []

        self._binary_path = app_root / config["Model"]["binary"]
        self._binary_args = config["Model"]["args"]

        self._sample_groups: dict[str, SampleGroup] = {}

    def prepare_for_testing(self) -> None:
        """
        Verifies that the binary can be found, loads both the sampling and analysis
        plugins, gets all sampling groups from their respective plugins, and makes an
        estimate for how long testing will take. 
        
        :param self: The instance of the class in which this method is called
        """

        event_bus.fire_event(Event.INITIALIZE)

        self._load_binary()

        self._load_sampling_plugins()
        self._load_analysis_plugins()

        self._sample_groups, sample_count = self._sample_from_plugins()

        self._estimate_testing_time(sample_count)

    def test_model(self) -> None:
        """
        Runs through the testing loop, iteratively testing each SampleGroup. For each
        SampleGroup, it resets the parameters file to its defaults, iteratively tests
        each Sample inside each group, and sends the resulting test data for the entire
        group of samples to the SampleGroupAnalyzer as a Table. For each Sample, it
        sets the parameters file to the values specified by the sample, runs the binary,
        and sends the resulting test data along with the reference data to the
        PerSampleAnalyzer. 

        :param self: The instance of the class in which this method is called
        """

        group_count = len(self._sample_groups)

        for group_index, (group_name, sample_group) in enumerate(
            self._sample_groups.items()
        ):
            event_bus.fire_event(
                Event.BEGAN_SAMPLING_FROM_GROUP,
                group_name=group_name,
                group_index=group_index,
                group_count=group_count
            )
            self._test_with_group(sample_group)

        self._param_editor.modify_parameters(self._defaults)
        event_bus.fire_event(Event.TESTING_COMPLETED)

    def _load_binary(self) -> None:
        binary_name = self._binary_path.name

        event_bus.fire_event(Event.LOADING_BINARY, binary_name=binary_name)

        try:
            self._binary_runner.load_binary(self._binary_path, self._binary_args)
        except FileNotFoundError as error:
            event_bus.fire_event(Event.BINARY_LOAD_FAILURE, reason=error)
            sys.exit(1)

        event_bus.fire_event(Event.BINARY_LOAD_SUCCESS)

    def _load_sampling_plugins(self) -> None:
        event_bus.fire_event(Event.BEGAN_LOADING_SAMPLING_PLUGINS)

        self._sampler_loader.load_plugins()

        plugins_loaded = self._sampler_loader.get_total_plugins_loaded_count()

        if not plugins_loaded:
            event_bus.fire_event(Event.SAMPLING_PLUGINS_LOAD_FAILURE)
            sys.exit(1)

        event_bus.fire_event(Event.SAMPLING_PLUGINS_LOAD_SUCCESS, count=plugins_loaded)

    def _load_analysis_plugins(self) -> None:
        event_bus.fire_event(Event.BEGAN_LOADING_ANALYSIS_PLUGINS)

        self._analyzer_loader.load_plugins()

        plugins_loaded = self._analyzer_loader.get_total_plugins_loaded_count()

        if not plugins_loaded:
            event_bus.fire_event(Event.ANALYSIS_PLUGINS_LOAD_FAILURE)
            sys.exit(1)

        event_bus.fire_event(Event.ANALYSIS_PLUGINS_LOAD_SUCCESS, count=plugins_loaded)

    def _sample_from_plugins(self) -> tuple[dict[str, SampleGroup], int]:
        event_bus.fire_event(Event.BEGAN_SAMPLE_GENERATION)
        
        sample_groups = self._sampler_loader.sample_from_plugins()

        if not sample_groups:
            event_bus.fire_event(Event.SAMPLING_FROM_PLUGINS_FAILURE)
            sys.exit(1)

        group_count = len(sample_groups)
        sample_count = self._count_group_samples(sample_groups)

        event_bus.fire_event(
            Event.SAMPLING_FROM_PLUGINS_SUCCESS,
            group_count=group_count,
            sample_count=sample_count
        )

        return (sample_groups, sample_count)

    def _count_group_samples(self, sample_groups: dict[str, SampleGroup]) -> int:
        count = 0

        for group in sample_groups.values():
            count += len(group)

        return count

    def _estimate_testing_time(self, sample_count: int) -> None:
        binary_name = self._binary_runner.get_binary_name()
        self._param_editor.modify_parameters(self._defaults)
        
        event_bus.fire_event(Event.BEGAN_TIMING_BINARY, binary_name=binary_name)

        start = time.time()
        exit_code = self._binary_runner.run_binary()
        end = time.time()

        if exit_code:
            event_bus.fire_event(Event.TIMING_BINARY_FAILURE, exit_code=exit_code)
            return

        seconds_estimated = (end - start) * sample_count

        event_bus.fire_event(
            Event.TIMING_BINARY_SUCCESS,
            seconds_estimate=seconds_estimated
        )

    def _test_with_group(self, group: SampleGroup) -> None:
        self._param_editor.modify_parameters(self._defaults)
        sample_count = len(group)

        for index, sample in enumerate(group):
            event_bus.fire_event(
                Event.SAMPLE_GENERATED,
                sample_index=index,
                sample_count=sample_count,
                sample=sample
            )

            self._test_with_sample(sample)

        if (not self._analyzer_loader.any_group_plugins_loaded()
                or not self._group_data
        ):
            return

        event_bus.fire_event(Event.BEGAN_GROUP_ANALYSIS)

        self._analyzer_loader.run_group_analysis(
            group,
            self._reference_data,
            self._group_data,
        )
        self._group_data = []

    def _test_with_sample(self, sample: Sample) -> None:
        binary_name = self._binary_runner.get_binary_name()

        self._param_editor.modify_parameters(sample.get_changed_values())

        event_bus.fire_event(Event.RUNNING_BINARY, binary_name=binary_name)
        exit_code = self._binary_runner.run_binary()
        event_bus.fire_event(Event.BINARY_EXITED, exit_code=exit_code)

        if exit_code:
            masked_data = MaskedModelData(self._output_file_reader.get_reference_data())
            self._group_data.append(masked_data)
            return

        test_data = self._output_file_reader.read_sample_data()
        self._group_data.append(test_data)

        if not self._analyzer_loader.any_sample_plugins_loaded():
            return

        event_bus.fire_event(Event.BEGAN_SAMPLE_ANALYSIS)

        self._analyzer_loader.run_sample_analysis(
            sample,
            self._reference_data,
            test_data
        )
