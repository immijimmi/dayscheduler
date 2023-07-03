from tkcomponents import Component
from tkcomponents.extensions import GridHelper, DragAndDrop

from tkinter import Button
from functools import partial
from typing import Callable, Union

from .enums import EntryKey
from .workspaceentry import WorkspaceEntry
from .timelineentry import TimelineEntry
from .workspacebin import WorkspaceBin


class Workspace(Component.with_extensions(GridHelper, DragAndDrop)):
    GRID_MINSIZES = (150, 2, 75)  # (column 0, divider rows, bin row)

    def __init__(self, scheduler, container, on_change: Callable[[tuple[int, int]], None], styles=None):
        super().__init__(container, on_change=on_change, styles=styles)

        styles = styles or {}
        self.styles["button"] = styles.get("button", {})
        self.styles["entry_frame"] = styles.get("entry_frame", {})
        self.styles["bin_frame"] = styles.get("bin_frame", {})
        self.styles["string_editor"] = styles.get("string_editor", {})
        self.styles["number_stepper"] = styles.get("number_stepper", {})
        self.styles["non_pending"] = styles.get("non_pending", {})
        self.styles["pending"] = styles.get("pending", {})
        self.styles["entry_non_pending"] = styles.get("entry_non_pending", {})
        self.styles["entry_pending"] = styles.get("entry_pending", {})
        self.styles["bin_non_pending"] = styles.get("bin_non_pending", {})
        self.styles["bin_pending"] = styles.get("bin_pending", {})

        self.scheduler = scheduler
        self.state = self.scheduler.state

        self._is_pending = False

    def _render(self) -> None:
        def on_change_workspace_entry(workspace_entry, change_key: EntryKey) -> None:
            workspace_entries_data = self.state.registered_get("workspace_entries")
            workspace_entry_data = workspace_entries_data[workspace_entry.index]

            if change_key is EntryKey.TITLE:
                workspace_entry_data[EntryKey.TITLE] = workspace_entry.title
            elif change_key is EntryKey.DURATION_M:
                workspace_entry_data[EntryKey.DURATION_M] = workspace_entry.duration_m

            workspace_entries_data[workspace_entry.index] = workspace_entry_data

            self.state.registered_set(workspace_entries_data, "workspace_entries")

        def on_change_workspace_bin(entry_key: Union[tuple[int, int], int]) -> None:
            if type(entry_key) is int:  # Entry to delete is in workspace
                workspace_entries = self.state.registered_get("workspace_entries")
                del workspace_entries[entry_key]

                self.state.registered_set(workspace_entries, "workspace_entries")
                self.render()

            else:  # Entry to delete is in timeline
                timeline_entry_key = f"{entry_key[0]}:{entry_key[1]}"

                timeline_entries = self.state.registered_get("timeline_entries")
                del timeline_entries[timeline_entry_key]

                self.state.registered_set(timeline_entries, "timeline_entries")
                self.scheduler.render()

        self.children["plus_button"] = None
        self.children["entries"] = []
        self.children["bin"] = None

        entries_data = self.state.registered_get("workspace_entries")

        stretch_row = (len(entries_data)*2)+1
        divider_rows = (*range(1, len(entries_data)*2, 2),)

        self._apply_frame_stretch(columns=(0,), rows=(stretch_row,))
        self._apply_dividers(self.GRID_MINSIZES[0], columns=(0,))
        self._apply_dividers(self.GRID_MINSIZES[1], rows=divider_rows)
        self._apply_dividers(self.GRID_MINSIZES[2], rows=(stretch_row+1,))

        plus_button = Button(self._frame, text="+", command=self._on_click_plus_button, **self.styles["button"])
        self.children["plus_button"] = plus_button
        plus_button.grid(row=0, column=1, sticky="nswe")

        for entry_index, entry_data in enumerate(entries_data):
            entry = WorkspaceEntry(
                self._frame,
                get_data=partial(
                    lambda x, y, z, workspace_entry_obj: (x, y, z),
                    entry_index, entry_data[EntryKey.TITLE], entry_data[EntryKey.DURATION_M]
                ),
                on_change=on_change_workspace_entry,
                styles={
                    "frame": {
                        **self.styles["entry_frame"],
                        **self.styles["entry_non_pending"]
                    },
                    "string_editor": {
                        **self.styles["string_editor"]
                    },
                    "number_stepper": {
                        **self.styles["number_stepper"]
                    },
                    "non_pending": {**self.styles["entry_non_pending"]},
                    "pending": {**self.styles["entry_pending"]}
                }
            )
            self.children["entries"].append(entry)
            entry.render().grid(row=(entry_index*2)+2, column=0, columnspan=2, sticky="nswe")

        workspace_bin = WorkspaceBin(
            self._frame,
            on_change=on_change_workspace_bin,
            styles={
                "frame": {
                    **self.styles["bin_frame"],
                    **self.styles["bin_non_pending"],
                },
                "non_pending": {**self.styles["bin_non_pending"]},
                "pending": {**self.styles["bin_pending"]}
            }
        )
        self.children["bin"] = workspace_bin
        workspace_bin.render().grid(row=stretch_row+1, column=0, columnspan=2, sticky="nswe")

    def _on_click_plus_button(self):
        workspace_entries = self.state.registered_get("workspace_entries")

        new_entry = {EntryKey.TITLE: "", EntryKey.DURATION_M: 15}
        workspace_entries.append(new_entry)

        self.state.registered_set(workspace_entries, "workspace_entries")
        self.render()

    def dnd_accept(self, source, event):
        if issubclass(type(source), TimelineEntry):
            return self

    def dnd_enter(self, source, event):
        if issubclass(type(source), TimelineEntry):
            if not self._is_pending:
                self._is_pending = True
                self._frame.configure(**self.styles["pending"])

    def dnd_leave(self, source, event):
        if issubclass(type(source), TimelineEntry):
            if self._is_pending:
                self._is_pending = False
                self._frame.configure(**self.styles["non_pending"])

    def dnd_commit(self, source, event):
        if issubclass(type(source), TimelineEntry):
            if self._is_pending:
                self._is_pending = False
                self._frame.configure(**self.styles["non_pending"])

            self._on_change(source.start_time)
