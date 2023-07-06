from tkcomponents import Component
from tkcomponents.extensions import GridHelper, DragAndDrop

from functools import partial
from datetime import timedelta
from typing import Union

from .enums import EntryKey
from .timelineentry import TimelineEntry
from .timelinecell import TimelineCell
from .timelinemargincell import TimelineMarginCell


class Timeline(Component.with_extensions(GridHelper, DragAndDrop)):
    GRID_MINSIZES = (60, 200, 12)  # (column 0, column 1, all rows)

    def __init__(self, scheduler, container, get_data, styles=None):
        super().__init__(container, get_data=get_data, styles=styles)

        styles = styles or {}
        self.styles["cell_frame"] = styles.get("cell_frame", {})
        self.styles["margin_frame"] = styles.get("margin_frame", {})
        self.styles["margin_label"] = styles.get("margin_label", {})
        self.styles["entry_frame"] = styles.get("entry_frame", {})
        self.styles["entry_label"] = styles.get("entry_label", {})
        self.styles["entry_label_period"] = styles.get("entry_label_period", {})
        self.styles["entry_label_title"] = styles.get("entry_label_title", {})
        self.styles["entry_label_title_compact"] = styles.get("entry_label_title_compact", {})
        self.styles["even_non_pending"] = styles.get("even_non_pending", {})
        self.styles["even_pending"] = styles.get("even_pending", {})
        self.styles["odd_non_pending"] = styles.get("odd_non_pending", {})
        self.styles["odd_pending"] = styles.get("odd_pending", {})
        self.styles["entry_non_pending"] = styles.get("entry_non_pending", {})
        self.styles["entry_pending"] = styles.get("entry_pending", {})

        self.scheduler = scheduler
        self.state = self.scheduler.state

    def _render(self) -> None:
        def on_change_timelinecell(
                old_data: Union[tuple[int, int], int],
                new_entry_position: tuple[int, int]
        ):
            if type(old_data) is int:  # old_data is a `self.index` from a WorkspaceEntry object
                new_key = f"{new_entry_position[0]}:{new_entry_position[1]}"

                current_timeline_entries = self.state.registered_get("timeline_entries")
                current_workspace_entries = self.state.registered_get("workspace_entries")

                if new_key in current_timeline_entries:
                    raise RuntimeError("unable to move a timeline entry to an already occupied location")
                else:
                    current_timeline_entries[new_key] = current_workspace_entries[old_data]
                    del current_workspace_entries[old_data]

                    if not self._is_timeline_data_valid(current_timeline_entries):
                        pass
                    else:
                        self.state.registered_set(current_timeline_entries, "timeline_entries")
                        self.state.registered_set(current_workspace_entries, "workspace_entries")
                        self.scheduler.render()

            else:  # old_data is a `timeline_position` from a TimelineEntry object
                old_key = f"{old_data[0]}:{old_data[1]}"
                new_key = f"{new_entry_position[0]}:{new_entry_position[1]}"

                current_timeline_entries = self.state.registered_get("timeline_entries")

                if new_key in current_timeline_entries:
                    raise RuntimeError("unable to move a timeline entry to an already occupied location")
                else:
                    current_timeline_entries[new_key] = current_timeline_entries[old_key]
                    del current_timeline_entries[old_key]

                    if not self._is_timeline_data_valid(current_timeline_entries):
                        pass
                    else:
                        self.state.registered_set(current_timeline_entries, "timeline_entries")
                        self.render()

        self.children["cells"] = {}  # Cells should be indexed by a tuple of (column_index, timeline_position)

        timeline_limits = self._get_data(self)

        column_indices = (0, 1)
        row_indices = tuple(range(
            0,
            (timeline_limits[1] - timeline_limits[0])*4
        ))

        self._apply_frame_stretch(columns=column_indices, rows=row_indices)
        self._apply_dividers(self.GRID_MINSIZES[0], columns=(0,))
        self._apply_dividers(self.GRID_MINSIZES[1], columns=(1,))
        self._apply_dividers(self.GRID_MINSIZES[2], rows=row_indices)

        timeline_entries = self.state.registered_get("timeline_entries")

        existing_entry_remaining_m = 0  # Used in loop to prevent overlapping entries in timeline
        for column_index in column_indices:
            for row_index in row_indices:
                curr_hr = int(timeline_limits[0] + (row_index / 4))
                curr_m = (row_index % 4) * 15
                timeline_position = (curr_hr, curr_m)

                hour_parity = "even" if ((row_index % 8) < 4) else "odd"

                if column_index == 0:  # Margin column
                    if curr_m == 0:
                        cell = TimelineMarginCell(
                            self._frame,
                            # `partial` is used to freeze the current value of `timeline_position` within the lambda
                            get_data=partial(lambda x, timeline_margin_cell_obj: x, timeline_position),
                            styles={
                                "frame": {
                                    **self.styles["margin_frame"],
                                    **self.styles[f"{hour_parity}_non_pending"]
                                },
                                "label": {
                                    **self.styles["margin_label"],
                                    **self.styles[f"{hour_parity}_non_pending"]
                                }
                            }
                        )
                        self.children["cells"][(0, timeline_position)] = cell
                        cell.render().grid(row=row_index, column=column_index, rowspan=4, sticky="nswe")

                else:  # Entry column
                    timeline_entry_key = f"{curr_hr}:{curr_m}"  # Used to index a timeline entry from the state
                    if timeline_entry_key in timeline_entries:  # If this is the first row of a timeline entry
                        timeline_entry_data = timeline_entries[timeline_entry_key]
                        timeline_entry_title = timeline_entry_data[EntryKey.TITLE]
                        timeline_entry_duration_m = timeline_entry_data[EntryKey.DURATION_M]

                        timeline_entry_rows = int(timeline_entry_duration_m / 15)
                        existing_entry_remaining_m = (timeline_entry_duration_m - 15)

                        cell = TimelineEntry(
                            self._frame,
                            # `partial` is used to freeze the current values of the below variables within the lambda
                            get_data=partial(
                                lambda x, y, z, timeline_entry_obj: (x, y, z),
                                timeline_position, timeline_entry_title, timeline_entry_duration_m
                            ),
                            styles={
                                "frame": {
                                    **self.styles["entry_frame"],
                                    **self.styles["entry_non_pending"]
                                },
                                "label_period": {
                                    **self.styles["entry_label"],
                                    **self.styles["entry_label_period"],
                                    **self.styles["entry_non_pending"]
                                },
                                "label_title": {
                                    **self.styles["entry_label"],
                                    **self.styles["entry_label_title"],
                                    **self.styles["entry_non_pending"]
                                },
                                "label_title_compact": {
                                    **self.styles["entry_label"],
                                    **self.styles["entry_label_title_compact"],
                                    **self.styles["entry_non_pending"]
                                },
                                "non_pending": {**self.styles["entry_non_pending"]},
                                "pending": {**self.styles["entry_pending"]}
                            }
                        )
                        self.children["cells"][(1, timeline_position)] = cell
                        cell.render().grid(row=row_index, column=column_index, rowspan=timeline_entry_rows, sticky="nswe")

                    elif existing_entry_remaining_m:  # If this row is a continuation of a timeline entry
                        existing_entry_remaining_m -= 15

                    else:
                        cell = TimelineCell(
                            self._frame,
                            # `partial` is used to freeze the current value of `timeline_position` within the lambda
                            get_data=partial(lambda x, timeline_cell_obj: x, timeline_position),
                            on_change=on_change_timelinecell,
                            styles={
                                "frame": {
                                    **self.styles["cell_frame"],
                                    **self.styles[f"{hour_parity}_non_pending"]
                                },
                                "non_pending": {**self.styles[f"{hour_parity}_non_pending"]},
                                "pending": {**self.styles[f"{hour_parity}_pending"]}
                            }
                        )
                        self.children["cells"][(1, timeline_position)] = cell
                        cell.render().grid(row=row_index, column=column_index, sticky="nswe")

    @staticmethod
    def _is_timeline_data_valid(timeline_data: dict[str, dict]) -> bool:
        occupied_timeslots = set()
        for key, value in timeline_data.items():
            start_hr, start_m = (int(num) for num in key.split(":"))
            start_time = timedelta(hours=start_hr, minutes=start_m)

            duration_m = value[EntryKey.DURATION_M]

            for offset_m in range(0, duration_m, 15):
                timeslot = start_time + timedelta(minutes=offset_m)

                if timeslot in occupied_timeslots:
                    return False

                occupied_timeslots.add(timeslot)

        return True
