from tkcomponents import Component
from tkcomponents.basiccomponents import StringEditor, Stepper
from tkcomponents.extensions import GridHelper, DragAndDrop

from typing import Callable

from ..constants import Constants as AppConstants
from .enums import EntryKey


class WorkspaceEntry(Component.with_extensions(GridHelper, DragAndDrop)):
    def __init__(
            self, container,
            get_data: Callable[["WorkspaceEntry"], tuple[int, str, int]],
            on_change: Callable[["WorkspaceEntry", EntryKey], None],
            styles=None
    ):
        super().__init__(container, get_data=get_data, on_change=on_change, styles=styles)

        styles = styles or {}
        self.styles["string_editor"] = styles.get("string_editor", {})
        self.styles["stepper"] = styles.get("stepper", {})
        self.styles["stepper_button"] = styles.get("stepper_button", {})
        self.styles["stepper_label"] = styles.get("stepper_label", {})
        self.styles["non_pending"] = styles.get("non_pending", {})
        self.styles["pending"] = styles.get("pending", {})

        self.index, self.title, self.duration_m = self._get_data(self)

        self._is_pending = False

    def _render(self) -> None:
        def on_change_stringeditor(editor, old_value):
            new_value = editor.value
            self.title = new_value

            self._on_change(self, EntryKey.TITLE)

        def on_change_stepper(stepper_obj, step_amount):
            self.duration_m += step_amount

            self._on_change(self, EntryKey.DURATION_M)

        self.children["string_editor"] = None
        self.children["stepper"] = None

        self._apply_frame_stretch(columns=(0,))
        self._apply_dividers(AppConstants.DIVIDER_SIZE_LARGE, rows=(1,))

        string_editor = StringEditor(
            self._frame,
            get_data=lambda stringeditor_obj: self.title,
            on_change=on_change_stringeditor,
            styles={
                "entry": {**self.styles["string_editor"]}
            }
        )
        self.children["string_editor"] = string_editor
        string_editor.render().grid(row=0, column=0, sticky="nswe")

        stepper = Stepper(
            self._frame,
            get_data=lambda stepper_obj: self.duration_m,
            on_change=on_change_stepper,
            before_steps=(("-1h", -60), ("-15m", -15)),
            after_steps=(("+15m", 15), ("+1h", 60)),
            format_label=lambda stepper_obj: f"{stepper_obj.value // 60:02}:{stepper_obj.value % 60:02}",
            limits=(15, None),
            styles={
                "button": {
                    **self.styles["stepper"],
                    **self.styles["stepper_button"]
                },
                "label": {
                    **self.styles["stepper"],
                    **self.styles["stepper_label"]
                }
            }
        )
        self.children["stepper"] = stepper
        stepper.render().grid(row=2, column=0, sticky="nswe")

        self.add_draggable_widget(self._frame)

    def dnd_accept(self, source, event):
        return self

    def dnd_leave(self, source, event):
        if source is self:
            if not self._is_pending:
                self._is_pending = True

                self._frame.configure(**self.styles["pending"])

    def dnd_end(self, source, event):  # If this entry ceases being dragged
        if self._is_pending:
            self._is_pending = False

            if self.exists:  # Prevents an exception if component is destroyed and re-rendered before this point
                self._frame.configure(**self.styles["non_pending"])
