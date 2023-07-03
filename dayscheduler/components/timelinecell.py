from tkcomponents import Component
from tkcomponents.extensions import DragAndDrop

from typing import Callable, Union

from .timelineentry import TimelineEntry
from .workspaceentry import WorkspaceEntry


class TimelineCell(Component.with_extensions(DragAndDrop)):
    def __init__(
            self, container,
            get_data: Callable[["TimelineCell"], tuple[int, int]],
            on_change: Callable[[Union[tuple[int, int], int], tuple[int, int]], None],
            styles=None
    ):
        super().__init__(container, get_data=get_data, on_change=on_change, styles=styles)

        styles = styles or {}
        self.styles["non_pending"] = styles.get("non_pending", {})
        self.styles["pending"] = styles.get("pending", {})

        self._is_pending = False

    def _render(self) -> None:
        pass

    def dnd_accept(self, source, event):
        if issubclass(type(source), TimelineEntry) or issubclass(type(source), WorkspaceEntry):
            return self

    def dnd_enter(self, source, event):
        if issubclass(type(source), TimelineEntry) or issubclass(type(source), WorkspaceEntry):
            if not self._is_pending:
                self._is_pending = True
                self._frame.configure(**self.styles["pending"])

    def dnd_leave(self, source, event):
        if issubclass(type(source), TimelineEntry) or issubclass(type(source), WorkspaceEntry):
            if self._is_pending:
                self._is_pending = False
                self._frame.configure(**self.styles["non_pending"])

    def dnd_commit(self, source, event):
        if issubclass(type(source), TimelineEntry):
            if self._is_pending:
                self._is_pending = False
                self._frame.configure(**self.styles["non_pending"])

            self._on_change(source.start_time, self._get_data(self))

        elif issubclass(type(source), WorkspaceEntry):
            if self._is_pending:
                self._is_pending = False
                self._frame.configure(**self.styles["non_pending"])

            self._on_change(source.index, self._get_data(self))
