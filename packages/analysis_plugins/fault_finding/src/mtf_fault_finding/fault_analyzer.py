from collections.abc import Iterable, Mapping, Sequence
from configparser import ConfigParser
import inspect
from pathlib import Path
import sys
from typing import Callable

import numpy.typing as npt

from mtf import root
from mtf.analysis import PerSampleAnalyzer
from mtf.output.file_utils import FileSystemTree
from mtf.sampling import Sample
from mtf.testing import ModelData
from mtf.util import ScopedImporter

from mtf_fault_finding import output
from mtf_fault_finding.check_status import CheckStatus

_CONFIG_PATH = root.get_config_path(
    root.ConfigPath.ANALYSIS_PLUGINS
) / "fault_finding.ini"
_CONFIG = ConfigParser()
_CONFIG.read(_CONFIG_PATH)

_SEPERATORS = ["%", "__"]


class _CheckFunction:
    def __init__(self, name: str, function: Callable):
        self._name = name
        self._function = function
        self._args: Iterable[str] = inspect.signature(function).parameters.keys()

    def call(
            self,
            data: Mapping[str, float | npt.NDArray]
    ) -> tuple[CheckStatus, None | str | Exception]:
        try:
            relevant_args = self._get_relevant_args(data)

            returned_status = self._function(**relevant_args)
            if returned_status is not None:
                match returned_status:
                    case CheckStatus.PASSED:
                        return (CheckStatus.PASSED, None)
                    case CheckStatus.SKIPPED:
                        return (CheckStatus.SKIPPED, None)
                    case CheckStatus.FAILED:
                        return (
                            CheckStatus.FAILED, (
                                "Check manually returned FAILED status, prefer using "
                                "an assertion instead"
                            )
                        )
                    case CheckStatus.ERROR:
                        return (
                            CheckStatus.ERROR,
                            Exception(
                                "Check manually returned ERROR status, prefer raising "
                                "an Exception instead"
                            )
                        )
            return (CheckStatus.PASSED, None)
        except AssertionError as assertion:
            message = ""
            if len(assertion.args) > 0:
                message = assertion.args[0]
            
            return (CheckStatus.FAILED, message)
        except Exception as error:
            return (CheckStatus.ERROR, error)

    def get_name(self) -> str:
        return self._name

    def _get_relevant_args(
            self,
            data: Mapping[str, float | npt.NDArray]
    ) -> Mapping[str, float | npt.NDArray]:
        relevant_args: dict[str, float | npt.NDArray] = {}

        for arg in self._args:
            if arg == "kwargs":
                continue
            if arg not in data:
                raise KeyError(
                    f"Requested argument {arg} not in avaliable arguments "
                    f"{list(data.keys())}"
                )
            relevant_args[arg] = data[arg]

        # Check is done after to avoid situation where check function specifies an
        # unavaliable argument AND kwargs.
        if "kwargs" in self._args:
            return data

        return relevant_args


class FaultAnalyzer(PerSampleAnalyzer):
    _CHECK_IDENTIFIER = "check"
    _CHECKS_PATH = root.get_app_root() / _CONFIG["Paths"]["checks_directory"]
    _PYTHON_EXTENSION = ".py"

    _REFERENCE_PARAM_PREFIX = "ref_"
    _TEST_PARAM_PREFIX = "test_"

    def __init__(self):
        self._checks = self._find_check_functions()

        if not self._checks:
            raise RuntimeError(f"No check functions found in {self._CHECKS_PATH}!")

    def analyze_sample_data(
        self,
        sample: Sample,
        reference_data: ModelData,
        test_data: ModelData, 
    ) -> tuple[str, FileSystemTree]:
        check_results: dict[str, tuple[CheckStatus, None | str | Exception]] = {}
        with reference_data, test_data:
            data = self._combine_data(sample, reference_data, test_data)

            for check in self._checks:
                check_result = check.call(data)
                check_results[check.get_name()] = check_result

        return output.generate_output(check_results)

    def _find_check_functions(self) -> list[_CheckFunction]:
        check_modules = self._find_check_modules()
        check_functions: list[_CheckFunction] = []

        test_importer = ScopedImporter(self._CHECKS_PATH)

        for module_path in check_modules:
            module = test_importer.import_module(module_path.stem)
            module_functions = inspect.getmembers(module, inspect.isfunction)

            for function_name, function in module_functions:
                if function_name.startswith(self._CHECK_IDENTIFIER):
                    check_functions.append(
                        _CheckFunction(function_name, function)
                    )

        return check_functions

    def _find_check_modules(self) -> list[Path]:
        check_module_paths: list[Path] = []

        for file in self._CHECKS_PATH.iterdir():
            if not file.is_file() or not file.suffix == self._PYTHON_EXTENSION:
                continue

            stem = file.stem
            if (not stem.startswith(self._CHECK_IDENTIFIER)
                and not stem.endswith(self._CHECK_IDENTIFIER)
            ):
                continue

            check_module_paths.append(file)

        return check_module_paths

    def _combine_data(
        self,
        sample: Mapping[str, float],
        reference_data: ModelData,
        test_data: ModelData
    ) -> dict[str, npt.NDArray]:
        data: dict[str, npt.NDArray] = dict(sample)

        for variable, values in reference_data.items():
            arg_name = self._REFERENCE_PARAM_PREFIX + self._clear_seperator(variable)
            data[arg_name] = values

        for variable, values in test_data.items():
            arg_name = self._TEST_PARAM_PREFIX + self._clear_seperator(variable)
            data[arg_name] = values

        return data

    def _clear_seperator(self, name: str) -> str:
        for seperator in _SEPERATORS:
            if seperator in name:
                return name.replace(seperator, "_")
        
        return name
