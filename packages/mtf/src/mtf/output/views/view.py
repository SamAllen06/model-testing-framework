from abc import ABC, abstractmethod
from collections.abc import Callable

from mtf.output.events import Event, event_bus


class View(ABC):
    def subscribe_to_bus(self) -> None:
        for event, callback in self._get_event_subscriptions().items():
            event_bus.subscribe(event, callback)


    @abstractmethod
    def _get_event_subscriptions(self) -> dict[Event, Callable[..., None]]:
        pass
