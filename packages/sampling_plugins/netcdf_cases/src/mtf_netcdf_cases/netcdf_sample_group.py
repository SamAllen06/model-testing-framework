from collections.abc import Iterator
from pathlib import Path

from netCDF4 import Dataset

from mtf.sampling import Sample, SampleGroup

CASES_DIMENSION = "cases"


class NetcdfSampleGroupIterator(Iterator):
    def __init__(self, group_file: Path):
        self._dataset = Dataset(group_file, "r", "NETCDF4")
        self._index = 0

    def __next__(self) -> Sample:
        if len(self._dataset.dimensions[CASES_DIMENSION]) == self._index:
            self._dataset.close()
            raise StopIteration()

        sample = _get_sample_from_dataset(self._dataset, self._index)
        self._index += 1
        return sample


class NetcdfSampleGroup(SampleGroup):
    def __init__(self, group_file: Path):
        self._validate_group_file(group_file)
        self._group_file = group_file

    def __getitem__(self, index: int | slice) -> Sample | list[Sample]:
        with Dataset(self._group_file, "r", "NETCDF4") as dataset:
            if isinstance(index, int):
                return _get_sample_from_dataset(dataset, index)
            elif isinstance(index, slice):
                samples = []
                for i in range(index.start, index.stop, index.step):
                    samples.append(_get_sample_from_dataset(dataset, i))

                return samples

    def __len__(self) -> int:
        with Dataset(self._group_file, "r", "NETCDF4") as dataset:
            return len(dataset.dimensions[CASES_DIMENSION])

    def __iter__(self) -> NetcdfSampleGroupIterator:
        return NetcdfSampleGroupIterator(self._group_file)

    def _validate_group_file(self, group_file: Path) -> None:
        with Dataset(group_file, "r", "NETCDF4") as dataset:
            for var in dataset.variables.values():
                if CASES_DIMENSION in var.dimensions:
                    break
            else:
                raise ValueError(
                    f"Expected group file {group_file} to use '{CASES_DIMENSION}' in "
                    "at least one variable"
                )


def _get_sample_from_dataset(dataset: Dataset, index: int) -> Sample:
    overrides = {}
    for var_name, var in dataset.variables.items():
        var_dimensions = var.dimensions
        if CASES_DIMENSION not in var_dimensions:
            continue

        var_slice = tuple(
            index if dim == CASES_DIMENSION else slice(None)
            for dim in var_dimensions
        )
        overrides[var_name] = var[var_slice]

    return Sample(overrides)
