from collections.abc import Sequence

from sampling.sample import Sample


# Effectively an immutable wrapper for a list of Samples. Useful for the immutability
# but also because "sample groups" have become a useful abstraction for other parts of 
# the program.
class SampleGroup(Sequence):
    def __init__(self, samples: Sequence[Sample]):
        self._samples = samples


    def __getitem__(self, index: int) -> Sample:
        return self._samples[index]


    def __len__(self) -> int:
        return len(self._samples)
