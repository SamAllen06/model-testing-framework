from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Mapping, Sized


class SampleGroupIterator(ABC, Iterator):
    @abstractmethod
    def __next__(self) -> Mapping[str, float]:
        pass


class SampleGroup(ABC, Iterable, Sized):
    @abstractmethod
    def get_sample_count(self) -> int:
        pass

    @abstractmethod
    def __iter__(self) -> SampleGroupIterator:
        pass

    def collapse_and_fill_down(self) -> list[dict[str, float]]:
        current_sample = {}
        result = []

        for sample in self:
            for key, value in sample.items():
                current_sample[key] = value
            result.append(current_sample.copy())

        return result

    def __len__(self) -> int:
        return self.get_sample_count()
