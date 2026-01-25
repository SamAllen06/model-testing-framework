from abc import ABC, abstractmethod

from sampling import SampleGroup

from sampling_libs.ranges import BoundTranslator


class Order(ABC):
    @abstractmethod
    def __init__(self, order_data, bound_translator: BoundTranslator):
        pass

    # This is the quickest way to make this plugin work with the new Sample API, this
    # plugin could use a rewrite in the future to make this implemention use Numpy 
    # features and better define order data types.
    @abstractmethod
    def to_sample_group(self) -> SampleGroup:
        pass
