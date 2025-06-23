from collections.abc import Iterable

from output.views import ConsoleView, FileView, LogsView, View, ViewType


def _view_factory(view_type: ViewType) -> View:
    match view_type:
        case ViewType.CONSOLE:
            return ConsoleView()
        case ViewType.FILE:
            return FileView()
        case ViewType.LOGS:
            return LogsView()


def enable_views(views: Iterable[ViewType]) -> None:
    for view_type in views:
        view = _view_factory(view_type)
        view.subscribe_to_bus()
