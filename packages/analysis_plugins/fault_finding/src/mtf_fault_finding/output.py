from collections import namedtuple
from io import StringIO
from pathlib import Path
import traceback
from typing import cast

from mtf.output.console_utils import ansi, indentation
from mtf.output.file_utils import FileReadType, FileSystemTree, table_to_csv
from mtf.util import Table

from mtf_fault_finding.check_status import CheckStatus

_STATUS_FILEPATH = Path("check_statuses.csv")
_FAILED_FILEPATH = Path("failed.csv")
_ERRORS_DIRECTORY = Path("errors")
_ERROR_FILENAME = "{check_name}.txt"


Summary = namedtuple("Summary", ["total", "passed", "skipped", "failed", "error"])


def generate_output(
    check_results: dict[str, tuple[CheckStatus, None | str | Exception]]
) -> tuple[str, FileSystemTree]:
    summary = _create_summary(check_results)

    console_output = _generate_console_output(summary)
    file_output = _generate_file_output(summary, check_results)

    return (console_output, file_output)

def _create_summary(
        check_results: dict[str, tuple[CheckStatus, None | str | Exception]]
) -> Summary:
    passed: set[str] = set()
    skipped: set[str] = set()
    failed: dict[str, str] = {}
    errored: dict[str, Exception] = {}

    for check_name, (status, data) in check_results.items():
        match (status):
            case CheckStatus.PASSED:
                passed.add(check_name)
            case CheckStatus.SKIPPED:
                skipped.add(check_name)
            case CheckStatus.FAILED:
                message = cast(str, data)
                failed[check_name] = message
            case CheckStatus.ERROR:
                error = cast(Exception, data)
                errored[check_name] = error

    return Summary(len(check_results), passed, skipped, failed, errored)

def _generate_console_output(summary: Summary) -> str:
    summary_formatting = [
        (len(summary.passed), "PASSED", ansi.AnsiColor.BRIGHT_GREEN),
        (len(summary.skipped), "SKIPPED", ansi.AnsiColor.BRIGHT_BLACK),
        (len(summary.failed), "FAILED", ansi.AnsiColor.BRIGHT_RED),
        (len(summary.error), "ERROR", ansi.AnsiColor.BRIGHT_YELLOW),
    ]

    summary_header = f"Results ({summary.total} checks run):"
    summary_lines: list[str] = []
    for count, status_name, color in summary_formatting:
        if count == 0:
            continue
        summary_lines.append(ansi.with_ansi_color(
            f"[{status_name}]: {count} checks", color
        ))

    summary_section = (
        summary_header
        + "\n"
        + indentation.with_indentation("\n".join(summary_lines))
    )

    failed_lines = []
    for check_name, message in summary.failed.items():
        failed_lines.append(f"[FAILED]: {check_name}")
        if message:
            failed_lines.append(indentation.with_indentation(message))

    error_lines = []
    for check_name, error in summary.error.items():
        error_lines.append(f"[ERROR]: {check_name}")
        error_lines.append(_format_traceback(error))

    failed_section = ansi.with_ansi_color(
        "\n".join(failed_lines), ansi.AnsiColor.BRIGHT_RED
    )
    error_section = ansi.with_ansi_color(
        "\n".join(error_lines), ansi.AnsiColor.BRIGHT_YELLOW
    )

    return "\n\n".join([summary_section, failed_section, error_section])


def _generate_file_output(
    summary: Summary,
    check_results: dict[str, tuple[CheckStatus, None | str | Exception]]
) -> FileSystemTree:
    files: dict[Path, StringIO] = {}

    files |= _generate_status_file(check_results)
    if summary.failed:
        files |= _generate_failed_file(summary.failed)
    if summary.error:
        files |= _generate_error_files(summary.error)

    return FileSystemTree.create_from_files(files)

def _generate_status_file(
    check_results: dict[str, tuple[CheckStatus, None | str | Exception]]
) -> dict[Path, tuple[FileReadType, list[StringIO]]]:
    statuses_table: Table[dict[str, list[str]], list[str]] = Table({}, [])
    statuses_sequence = statuses_table.as_sequence()
    statuses_sequence.initialize_keys(["check", "status"])

    for check, result in check_results.items():
        status_name = result[0].name
        check_status_entry = {"check": check, "status": status_name}
        statuses_sequence.append(check_status_entry)

    status_file_contents = table_to_csv.convert_to_csv_data(statuses_table)
    return {_STATUS_FILEPATH: (FileReadType.IN_MEMORY, [status_file_contents])}

def _generate_failed_file(failed: dict[str, str]) -> dict[Path, StringIO]:
    failed_table: Table[dict[str, list[str]], list[str]] = Table({}, [])
    failed_sequence = failed_table.as_sequence()
    failed_sequence.initialize_keys(["check", "message"])

    for check, message in failed.items():
        failed_sequence.append({"check": check, "message": message})

    failed_file_contents = table_to_csv.convert_to_csv_data(failed_sequence)
    return {_FAILED_FILEPATH: (FileReadType.IN_MEMORY, [failed_file_contents])}

def _generate_error_files(errored: dict[str, Exception]) -> dict[Path, StringIO]:
    files: dict[Path, StringIO] = {}

    for check, error in errored.items():
        filepath = _ERRORS_DIRECTORY / _ERROR_FILENAME.format(check_name=check)
        file_contents = StringIO()

        formatted_exception = _format_traceback(error)
        file_contents.write(formatted_exception)

        files[filepath] = (FileReadType.IN_MEMORY, [file_contents])

    return files

def _format_traceback(error: Exception) -> str:
    traceback_lines = traceback.format_exception(error)
    # The second line is the plugin calling the check.
    traceback_lines.pop(1)
    return "".join(traceback_lines)

