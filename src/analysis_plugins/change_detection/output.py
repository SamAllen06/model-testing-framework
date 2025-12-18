from pathlib import Path

from output.console_utils import indentation
from output.file_utils import FileReadType, FileSystemTree, list_to_txt


def make_output(inputs: set[str], outputs: set[str]) -> tuple[str, FileSystemTree]:
    return (
        _make_console_output(inputs, outputs),
        _make_file_output(inputs, outputs),
    )


def _make_console_output(inputs: set[str], outputs: set[str]) -> str:
    lines = []

    lines.append(
        f"Changes to {len(outputs)} outputs observed resulting from changes to "
        f"{len(inputs)} inputs.\n"
    )

    lines.append("Inputs:")

    for input in inputs:
        lines.append(indentation.with_indentation(input, 1))
    
    lines.append("")

    lines.append("Outputs:")

    for output in outputs:
        lines.append(indentation.with_indentation(output, 1))

    return "\n".join(lines)


def _make_file_output(inputs: set[str], outputs: set[str]) -> FileSystemTree:
    files = {
        Path("inputs.txt"): (
            FileReadType.IN_MEMORY,
            [list_to_txt.convert_to_txt_data(list(inputs))],
        ),
        Path("outputs.txt"): (
            FileReadType.IN_MEMORY,
            [list_to_txt.convert_to_txt_data(list(outputs))],
        ),
    }

    return FileSystemTree.create_from_files(files)
