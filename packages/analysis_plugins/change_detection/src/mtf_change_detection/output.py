from pathlib import Path

from mtf.output.console_utils import indentation
from mtf.output.file_utils import FileReadType, FileSystemTree, list_to_txt


def make_output(constants: set[str], outputs: set[str]) -> tuple[str, FileSystemTree]:
    return (
        _make_console_output(constants, outputs),
        _make_file_output(constants, outputs),
    )


def _make_console_output(constants: set[str], outputs: set[str]) -> str:
    lines = []

    lines.append(
        f"Changes to {len(outputs)} outputs observed resulting from changes to "
        f"{len(constants)} constants.\n"
    )

    lines.append("Constants:")

    for input in constants:
        lines.append(indentation.with_indentation(input, 1))
    
    lines.append("")

    lines.append("Outputs:")

    for output in outputs:
        lines.append(indentation.with_indentation(output, 1))

    return "\n".join(lines)


def _make_file_output(constants: set[str], outputs: set[str]) -> FileSystemTree:
    files = {
        Path("constants.txt"): (
            FileReadType.IN_MEMORY,
            [list_to_txt.convert_to_txt_data(list(constants))],
        ),
        Path("outputs.txt"): (
            FileReadType.IN_MEMORY,
            [list_to_txt.convert_to_txt_data(list(outputs))],
        ),
    }

    return FileSystemTree.create_from_files(files)
