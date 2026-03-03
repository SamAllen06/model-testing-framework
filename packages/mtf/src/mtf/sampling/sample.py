from collections.abc import Iterator, Mapping

import numpy.typing as npt


class Sample(Mapping):
    # Only values differing from the defaults need to be provided.
    def __init__(self, values: Mapping[str, npt.NDArray]):
        self._ensure_in_defaults(values)
        self._values = values


    @classmethod
    def set_defaults(cls, defaults: Mapping[str, npt.NDArray]) -> None:
        cls._defaults = defaults


    # For instances when we only want to use the values that differ from the defaults.
    def get_changed_values(self) -> Mapping[str, npt.NDArray]:
        return self._values


    def __getitem__(self, const_name: str) -> npt.NDArray:
        if const_name in self._values:
            return self._values[const_name]
        elif const_name in self._defaults:
            return self._defaults[const_name]
        else:
            raise KeyError(f"Sample does not have a constant named {const_name}")


    def __iter__(self) -> Iterator:
        all_values = self._defaults.copy()
        all_values.update(self._values)
        return iter(all_values)


    def __len__(self) -> int:
        return len(self._defaults)


    def _ensure_in_defaults(self, values: Mapping[str, npt.NDArray]) -> None:
        for const in values:
            if const not in self._defaults:
                # If we instead allowed Samples to use constants not defined in the 
                # defaults, the program wouldn't be able to handle when another sample,
                # possibly from another plugin, doesn't have a value for that constant.
                # Additionally, it would break __iter__ and __len__.
                raise KeyError(f"Constant {const} has not been assigned a default")
