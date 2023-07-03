from tkcomponents import Component
from tkcomponents.extensions import GridHelper, DragAndDrop

from tkinter import Label
from typing import Callable
from datetime import timedelta

from ..constants import Constants as AppConstants


class TimelineEntry(Component.with_extensions(GridHelper, DragAndDrop)):
    COMPACT_CELLS_LIMIT = 3

    def __init__(self, container, get_data: Callable[["TimelineEntry"], tuple[tuple[int, int], str, int]], styles=None):
        super().__init__(container, get_data=get_data, styles=styles)

        styles = styles or {}
        self.styles["label_period"] = styles.get("label_period", {})
        self.styles["label_title"] = styles.get("label_title", {})
        self.styles["label_title_compact"] = styles.get("label_title_compact", {})
        self.styles["non_pending"] = styles.get("non_pending", {})
        self.styles["pending"] = styles.get("pending", {})

        self.start_time, self.title, self.duration_m = self._get_data(self)

        end_time = timedelta(hours=self.start_time[0], minutes=self.start_time[1]) + timedelta(minutes=self.duration_m)
        end_time_hours = int((end_time.days * 24) + (end_time.seconds // 3600))
        end_time_minutes = int((end_time.seconds % 3600) / 60)
        self.end_time = (end_time_hours, end_time_minutes)

        self._is_pending = False

    def _render(self) -> None:
        self.children["title_label"] = None
        self.children["period_label"] = None

        cells_occupied = int(self.duration_m/15)
        do_render_compact = (cells_occupied <= self.COMPACT_CELLS_LIMIT)

        if do_render_compact:
            self._apply_frame_stretch(rows=(1,), columns=(1,))
            self._apply_dividers(AppConstants.DIVIDER_SIZE_LARGE, columns=(1,))
        else:
            self._apply_frame_stretch(rows=(2,), columns=(0,))
            self._apply_dividers(AppConstants.DIVIDER_SIZE_LARGE, columns=(1,))

        # Title Label
        title_label = Label(
            self._frame, text=self.title,
            **{
                **self.styles[("label_title_compact" if do_render_compact else "label_title")],
                **self.styles["non_pending"]
            }
        )
        self.children["title_label"] = title_label

        if do_render_compact:
            title_label.grid(row=0, column=0, sticky="nw")
        else:
            title_label.grid(row=2, column=0, columnspan=3, sticky="sw")

        # Period Label
        period_label_text = (
            f"{self.start_time[0]:02}:{self.start_time[1]:02}" +
            " - " +
            f"{self.end_time[0]:02}:{self.end_time[1]:02}"
        )

        period_label = Label(
            self._frame, text=period_label_text,
            **{**self.styles["label_period"], **self.styles["non_pending"]}
        )
        self.children["period_label"] = period_label

        if do_render_compact:
            period_label.grid(row=0, column=2, sticky="ne")
        else:
            period_label.grid(row=0, column=2, sticky="ne")

        self.add_draggable_widget(self._frame, do_include_children=True)

    def dnd_accept(self, source, event):
        return self

    def dnd_leave(self, source, event):
        if source is self:
            if not self._is_pending:
                self._is_pending = True

                self._frame.configure(**self.styles["pending"])
                self.children["title_label"].configure(**self.styles["pending"])
                self.children["period_label"].configure(**self.styles["pending"])

    def dnd_end(self, source, event):  # If this entry ceases being dragged
        if self._is_pending:
            self._is_pending = False

            if self.exists:  # Prevents an exception if component is destroyed and re-rendered before this point
                self._frame.configure(**self.styles["non_pending"])
                self.children["title_label"].configure(**self.styles["non_pending"])
                self.children["period_label"].configure(**self.styles["non_pending"])
