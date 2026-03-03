from pathlib import Path
from tempfile import NamedTemporaryFile

from netCDF4 import Dataset

from mtf.output.console_utils import ansi
from mtf.output.file_utils import FileReadType, FileSystemTree, list_to_txt

from mtf.analysis_libs.diff_store import DifferenceStore

def generate_output(
        group_differences: list[DifferenceStore]
) -> tuple[str, FileSystemTree]:
    console_output = _generate_console_output(group_differences)
    file_output = _generate_file_output(group_differences)

    return (
        console_output,
        file_output,
    )


def _generate_console_output(group_differences: list[DifferenceStore]) -> str:
    lines = []

    difference_count = 0
    differing_variables = set()
    for differences in group_differences:
        if len(differences) == 0:
            continue

        difference_count += 1
        for variable in differences:
            differing_variables.add(variable)

    differing_variables = sorted(list(differing_variables))

    if difference_count:
        lines.append(
            f"{difference_count} samples differed from the reference on the following "
            "variables:"
        )
        for variable in differing_variables:
            lines.append(variable)
    else:
        lines.append(
            ansi.with_ansi_color(
                "No differences from the reference were found.",
                ansi.AnsiColor.BRIGHT_YELLOW,
            )
        )

    return "\n".join(lines)


def _generate_file_output(group_differences: list[DifferenceStore]) -> FileSystemTree:
    tfile = NamedTemporaryFile(delete=False)
    tfile.close()

    file_path = Path(tfile.name)
    with Dataset(file_path, "w", "NETCDF4") as dataset:
        pass

    return FileSystemTree.create_from_file(".nc", FileReadType.TEMP_FILE, [file_path])

