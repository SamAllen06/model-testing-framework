from abc import ABC, abstractmethod
from typing import Mapping

from sampling.sample_group import SampleGroup


class Sampler(ABC):
    """
    Returns a dictionary mapping each sample group's name to the SampleGroup object it 
    is represented by. 
    """

    @abstractmethod
    def get_sample_groups(self) -> Mapping[str, SampleGroup]:
        pass
