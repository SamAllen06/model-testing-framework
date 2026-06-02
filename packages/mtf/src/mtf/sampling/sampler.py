from abc import ABC, abstractmethod
from typing import Mapping

from mtf.sampling.sample_group import SampleGroup


class Sampler(ABC):
    """
    An abstract class that is meant to be subclassed once by each sampling plugin and
    provides an interface for returning SampleGroups.
    """

    @abstractmethod
    def get_sample_groups(self) -> Mapping[str, SampleGroup]:
        """
        Returns a dictionary mapping each sample group's name to the SampleGroup object it 
        is represented by. 
        """

        pass
