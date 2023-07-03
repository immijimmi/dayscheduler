from tkcomponents import Component
from tkcomponents.extensions import GridHelper

from tkinter import Label
from typing import Callable


class TimelineMarginCell(Component.with_extensions(GridHelper)):
    def __init__(self, container, get_data: Callable[["TimelineMarginCell"], tuple[int, int]], styles=None):
        super().__init__(container, get_data=get_data, styles=styles)

        styles = styles or {}
        self.styles["label"] = styles.get("label", {})

    def _render(self) -> None:
        self.children["label"] = None

        self._apply_frame_stretch(rows=(1,), columns=(1,))

        timeline_position = self._get_data(self)
        label_text = f"{timeline_position[0]:02}:{timeline_position[1]:02}"

        label = Label(self._frame, text=label_text, **self.styles["label"])
        self.children["label"] = label
        label.grid(row=0, column=0, sticky="nw")
