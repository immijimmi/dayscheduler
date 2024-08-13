from tkcomponents import Component
from tkcomponents.extensions import GridHelper
from managedstate import State
from managedstate.extensions import Registrar, Listeners

from .config import Config
from .components import Timeline, Workspace


class Scheduler(Component.with_extensions(GridHelper)):
    def __init__(self, container, config=Config):
        super().__init__(container)

        self._config = config

        # State Initialisation
        self.state = State.with_extensions(Registrar, Listeners)()
        self._register_paths()

    def _render(self) -> None:
        def on_change_workspace(timeline_entry_start_time: tuple[int, int]) -> None:
            timeline_entries = self.state.registered_get("timeline_entries")
            workspace_entries = self.state.registered_get("workspace_entries")

            timeline_entry_key = f"{timeline_entry_start_time[0]}:{timeline_entry_start_time[1]}"
            entry_data = timeline_entries[timeline_entry_key]

            workspace_entries.append(entry_data)
            del timeline_entries[timeline_entry_key]

            self.state.registered_set(timeline_entries, "timeline_entries")
            self.state.registered_set(workspace_entries, "workspace_entries")

            self.render()

        self.children["timeline"] = None
        self.children["workspace"] = None

        self._apply_frame_stretch(rows=(0,), columns=(0, 1))

        timeline = Timeline(
            self, self._frame,
            get_data=lambda timeline_obj: self._config.TIMELINE_LIMITS,
            styles=self._config.THEME["timeline"]
        )
        self.children["timeline"] = timeline
        timeline.render().grid(row=0, column=0, sticky="nswe")

        workspace = Workspace(
            self, self._frame,
            on_change=on_change_workspace,
            styles=self._config.THEME["workspace"]
        )
        self.children["workspace"] = workspace
        workspace.render().grid(row=0, column=1, sticky="nswe")

    def _register_paths(self):
        self.state.register_path("timeline_entries", ["timeline_entries"], [{}])
        self.state.register_path("workspace_entries", ["workspace_entries"], [[]])
