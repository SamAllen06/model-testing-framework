from collections.abc import Mapping, Sequence
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from netCDF4 import Dataset

from output.console_utils import ansi
from output.file_utils import FileReadType, FileSystemTree, list_to_txt

from .difference_store import DifferenceStore

def generate_output(differences: DifferenceStore) -> tuple[str, FileSystemTree]:
    console_output = _generate_console_output(differences)
    file_output = _generate_file_output(differences)

    return (
        console_output,
        file_output,
    )


def _generate_console_output(differences: DifferenceStore) -> str:
    lines: list[str] = []
    no_differences_flag = True

    for variable, diffs in differences.items():
        no_differences_flag = False
        variable_header = ansi.with_ansi_color(variable, ansi.AnsiColor.BRIGHT_CYAN)
        lines.append(variable_header)

        count = len(diffs.indices)
        lines.append(f"{count} differences from reference found.")

    if no_differences_flag:
        lines.append(
            ansi.with_ansi_color(
                "No differences from reference found.", ansi.AnsiColor.BRIGHT_YELLOW
            )
        )

    return "\n".join(lines)


def _generate_file_output(differences: DifferenceStore) -> FileSystemTree:
    files: dict[Path, tuple[FileReadType, list]] = {}
    for variable in differences:
        file_path = Path(variable + ".nc")
        files[file_path] = (FileReadType.TEMP_FILE, [
            _make_diffs_dataset(differences, variable)
        ])

    unchanged_variables = differences.get_unchanged_variables()
    if unchanged_variables:
        file_data = list_to_txt.convert_to_txt_data(unchanged_variables)
        files[Path("unchanged_variables.txt")] = (FileReadType.IN_MEMORY, [file_data])

    return FileSystemTree.create_from_files(files)


def _make_diffs_dataset(differences: DifferenceStore, variable: str) -> Path:
    tfile = NamedTemporaryFile(delete=False)
    tfile.close()

    file_path = Path(tfile.name)
    with Dataset(file_path, "w", "NETCDF4") as dataset:
        dimensions = differences.get_variable_dimensions(variable)
        indices, ref, test, diff = differences[variable]
        
        dataset.createDimension("diff_index", len(indices))

        for dimension, dimension_data in zip(dimensions, indices.T):
            ds_var = dataset.createVariable(
                f"{dimension}_index", indices.dtype, ("diff_index",),
                compression="zlib",
                shuffle=False,
                complevel=1,
            )

            ds_var[:] = dimension_data

        ref_var = dataset.createVariable(
            "ref", ref.dtype, ("diff_index",),
            compression="zlib",
            shuffle=True,
            complevel=3,
        )
        test_var = dataset.createVariable(
            "test", test.dtype, ("diff_index",),
            compression="zlib",
            shuffle=True,
            complevel=3,
        )
        diff_var = dataset.createVariable(
            "diff", diff.dtype, ("diff_index",),
            compression="zlib",
            shuffle=True,
            complevel=3,
        )

        ref_var[:] = ref
        test_var[:] = test
        diff_var[:] = diff

    return file_path

