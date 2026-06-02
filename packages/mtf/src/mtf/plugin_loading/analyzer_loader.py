from collections.abc import Mapping, Sequence
import importlib
import json
import pkgutil
import sys

from mtf import root
from mtf.output.events import Event, event_bus
from mtf.analysis import PerSampleAnalyzer, SampleGroupAnalyzer
from mtf.plugin_loading.plugin_loader import PluginLoader
from mtf.sampling import SampleGroup
from mtf.testing import ModelData


class AnalyzerLoader(PluginLoader):
    """
    A subclass of Plugin Loader which loads analysis plugins.

    Each analysis plugin must have an "analyzer_class" attribute, which stores a class
    that extends either PerSampleAnalyzer or SampleGroupAnalyzer.
    """

    def __init__(self):
        with open(root.get_config_path(root.ConfigPath.PLUGIN_WHITELIST), "r") as file:
            whitelist = json.load(file)

        super().__init__(
            [PerSampleAnalyzer, SampleGroupAnalyzer],
            "analyzer_class",
            whitelist["analysis"]
        )

    def any_sample_plugins_loaded(self) -> bool:
        """
        Gets whether any sample plugins have been loaded.
        
        :return: Whether any sample plugins have been loaded
        :rtype: bool
        """

        return len(self._plugin_objects[PerSampleAnalyzer]) > 0

    def any_group_plugins_loaded(self) -> bool:
        """
        Gets whether any group plugins have been loaded.
        
        :return: Whether any group plugins have been loaded.
        :rtype: bool
        """
        
        return len(self._plugin_objects[SampleGroupAnalyzer]) > 0

    def run_sample_analysis(
            self,
            sample: Mapping[str, float],
            reference_data: Mapping[str, Sequence[float]],
            test_data: Mapping[str, Sequence[float]]
    ) -> None:
        """
        Runs an analysis on an individual sample plugin.
        
        :param sample: A mapping of parameter names to their values
        :type sample: Mapping[str, float]
        :param reference_data: A mapping of parameter names to an ordered collection of
        reference data values
        :type reference_data: Mapping[str, Sequence[float]]
        :param test_data: A mapping of parameter names to an ordered collection of test
        data values
        :type test_data: Mapping[str, Sequence[float]]
        """
        
        for plugin_name, analyzer in self._plugin_objects[PerSampleAnalyzer].items():
            event_bus.fire_event(
                Event.BEGAN_SAMPLE_ANALYSIS_WITH_PLUGIN,
                plugin_name=plugin_name
            )

            try:
                console_out, file_out = analyzer.analyze_sample_data(
                    sample, reference_data, test_data
                )
                event_bus.fire_event(
                    Event.SAMPLE_ANALYSIS_WITH_PLUGIN_SUCCESS,
                    plugin_name=plugin_name,
                    console_output=console_out,
                    file_output=file_out
                )
            except Exception as error:
                event_bus.fire_event(
                    Event.SAMPLE_ANALYSIS_WITH_PLUGIN_FAILURE,
                    plugin_name=plugin_name,
                    reason=error
                )

    def run_group_analysis(
            self,
            sample_group: SampleGroup,
            reference_data: ModelData,
            sample_data: list[ModelData],
    ) -> None:
        """
        Runs an analysis on a sample group plugin.

        :param sample_group: A plugin that returns samples in a defined order to be
        tested
        :type sample_group: SampleGroup
        :param reference_data: A data file used to store data from the model
        :type reference_data: ModelData
        :param sample_data: A list of ModelData instances
        :type sample_data: list[ModelData]
        """

        for plugin_name, analyzer in self._plugin_objects[SampleGroupAnalyzer].items():
            event_bus.fire_event(
                Event.BEGAN_GROUP_ANALYSIS_WITH_PLUGIN,
                plugin_name=plugin_name
            )

            try:
                console_out, file_out = analyzer.analyze_sample_data(
                    sample_group, reference_data, sample_data
                )
                event_bus.fire_event(
                    Event.GROUP_ANALYSIS_WITH_PLUGIN_SUCCESS,
                    plugin_name=plugin_name,
                    console_output=console_out,
                    file_output=file_out
                )
            except Exception as error:
                event_bus.fire_event(
                    Event.GROUP_ANALYSIS_WITH_PLUGIN_FAILURE,
                    plugin_name=plugin_name,
                    reason=error
                )

    def _fire_loading_plugin_event(self, plugin_name: str) -> None:
        event_bus.fire_event(Event.LOADING_ANALYSIS_PLUGIN, plugin_name=plugin_name)

    def _fire_plugin_load_failed_event(self, plugin_name: str, error: Exception) -> None:
        event_bus.fire_event(
            Event.ANALYSIS_PLUGIN_LOAD_FAILURE,
            plugin_name=plugin_name,
            reason=error
        )

    def _fire_plugin_load_success_event(self, plugin_name: str) -> None:
        event_bus.fire_event(
            Event.ANALYSIS_PLUGIN_LOAD_SUCCESS,
            plugin_name=plugin_name
        )
