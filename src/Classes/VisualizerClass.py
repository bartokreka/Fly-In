"""Display a drone network and turn-by-turn drone positions."""

from __future__ import annotations

import math
import tkinter as tk
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from tkinter import messagebox, ttk

from .DroneClass import State
from .SimulationClass import Simulation


@dataclass(frozen=True)
class ZoneView:
    """Describe a zone for display.

    Attributes:
        name: Zone name.
        x: Horizontal map coordinate.
        y: Vertical map coordinate.
        color: Display color name, or None for the default color.
        zone_type: Zone type shown in the label.
        capacity: Maximum number of drones, or None for unlimited.
    """

    name: str
    x: int
    y: int
    color: str | None = None
    zone_type: str = "normal"
    capacity: int | None = 1


@dataclass(frozen=True)
class ConnectionView:
    """Describe a connection for display.

    Attributes:
        start: Name of the first endpoint zone.
        end: Name of the second endpoint zone.
        capacity: Maximum number of drones in transit at once.
    """

    start: str
    end: str
    capacity: int = 1


@dataclass(frozen=True)
class DroneView:
    """Describe a drone in a zone or on a connection.

    Attributes:
        name: Label drawn on the drone.
        zone: Name of the zone the drone is in, or None.
        connection: Endpoint names of the connection the drone is on, or
            None.
    """

    name: str
    zone: str | None = None
    connection: tuple[str, str] | None = None


@dataclass(frozen=True)
class Frame:
    """Describe the simulation state after one complete turn.

    Attributes:
        turn: Number of completed turns.
        drones: Drones that have not reached the end zone yet.
        delivered: Number of drones that reached the end zone.
        finished: True once every drone has been delivered.
    """

    turn: int
    drones: Sequence[DroneView]
    delivered: int
    finished: bool = False


class Visualizer:
    """Render simulation frames without changing movement rules."""

    def __init__(
        self,
        zones: Sequence[ZoneView],
        connections: Sequence[ConnectionView],
        initial_frame: Frame,
        next_frame: Callable[[], Frame],
        restart_frame: Callable[[], Frame],
    ) -> None:
        """Create the window, controls, and canvas.

        Args:
            zones: Zones to draw.
            connections: Connections to draw.
            initial_frame: State shown before the first turn.
            next_frame: Callback that advances the simulation by one turn
                and returns the new state.
        """
        self.zones = {zone.name: zone for zone in zones}
        self.connections = list(connections)
        self.frame = initial_frame
        self.next_frame = next_frame
        self.restart_frame = restart_frame

        self.positions: dict[str, tuple[float, float]] = {}
        self.playing = False
        self.timer: str | None = None

        self.root = tk.Tk()
        self.root.title("Fly-in — Drone simulation")
        self.root.geometry("1100x750")
        self.root.minsize(650, 450)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.delay = tk.IntVar(master=self.root, value=500)
        self.status = tk.StringVar(master=self.root)

        self._create_controls()

        self.canvas = tk.Canvas(
            self.root,
            background="#111827",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

        self._update_status()

    def _create_controls(self) -> None:
        """Create playback controls and the status label."""
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)

        self.next_button = ttk.Button(
            toolbar,
            text="Next turn",
            command=self.step,
        )
        self.next_button.pack(side=tk.LEFT)

        self.play_button = ttk.Button(
            toolbar,
            text="Play",
            command=self.toggle_play,
        )
        self.play_button.pack(side=tk.LEFT, padx=8)

        self.restart_button = ttk.Button(
            toolbar,
            text="Restart",
            command=self.restart,
        )
        self.restart_button.pack(side=tk.LEFT, padx=8)

        ttk.Label(toolbar, text="Delay (ms):").pack(side=tk.LEFT)

        ttk.Spinbox(
            toolbar,
            from_=50,
            to=3000,
            increment=50,
            textvariable=self.delay,
            width=7,
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(
            toolbar,
            textvariable=self.status,
        ).pack(side=tk.RIGHT)

        ttk.Label(
            self.root,
            text=(
                "Large circle: zone | Small circle: drone | "
                "Drone on a line: restricted transit | "
                "Zone label: occupancy / capacity"
            ),
            padding=(10, 0, 10, 8),
        ).pack(fill=tk.X)

    def _on_resize(self, _event: tk.Event) -> None:
        """Redraw the network after resizing.

        Args:
            _event: The Tk configure event, unused.
        """
        self._draw()

    def _calculate_positions(self) -> None:
        """Scale map coordinates while preserving their proportions."""
        self.positions.clear()
        if not self.zones:
            return

        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        margin = 85

        xs = [zone.x for zone in self.zones.values()]
        ys = [zone.y for zone in self.zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max_x - min_x
        span_y = max_y - min_y

        available_x = max(width - 2 * margin, 1)
        available_y = max(height - 2 * margin, 1)

        scales = []
        if span_x:
            scales.append(available_x / span_x)
        if span_y:
            scales.append(available_y / span_y)
        scale = min(scales) if scales else 1.0

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        for zone in self.zones.values():
            self.positions[zone.name] = (
                width / 2 + (zone.x - center_x) * scale,
                height / 2 - (zone.y - center_y) * scale,
            )

    def _safe_color(self, color: str | None) -> str:
        """Return a Tk color, falling back for unsupported names.

        Args:
            color: Requested color name, or None.

        Returns:
            ``color`` if Tk supports it, otherwise a default gray.
        """
        if color:
            try:
                self.root.winfo_rgb(color)
                return color
            except tk.TclError:
                pass
        return "#64748b"

    def _draw_connections(self) -> None:
        """Draw links behind the zones."""
        for connection in self.connections:
            x1, y1 = self.positions[connection.start]
            x2, y2 = self.positions[connection.end]

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#64748b",
                width=3,
            )

            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 - 16,
                text=f"link cap: {connection.capacity}",
                fill="#cbd5e1",
                font=("Arial", 9),
            )

    def _draw_zones(self) -> None:
        """Draw zone colors, types, and occupancy."""
        occupancy: dict[str, int] = defaultdict(int)
        for drone in self.frame.drones:
            if drone.zone is not None:
                occupancy[drone.zone] += 1

        for zone in self.zones.values():
            x, y = self.positions[zone.name]
            radius = 30

            self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=self._safe_color(zone.color),
                outline="#f8fafc",
                width=2,
            )

            capacity = (
                "unlimited" if zone.capacity is None
                else str(zone.capacity)
            )

            self.canvas.create_text(
                x, y + 47,
                text=(
                    f"{zone.name} [{zone.zone_type}]\n"
                    f"{occupancy[zone.name]} / {capacity}"
                ),
                fill="#f8fafc",
                font=("Arial", 10),
                justify=tk.CENTER,
            )

    def _draw_drone_group(
        self,
        drones: Sequence[DroneView],
        x: float,
        y: float,
    ) -> None:
        """Arrange drones around a shared position.

        Args:
            drones: Drones located at the same position.
            x: Horizontal canvas coordinate of the position.
            y: Vertical canvas coordinate of the position.
        """
        count = len(drones)
        ring_radius = 0.0 if count == 1 else max(
            17.0, count * 30 / math.tau
        )

        for index, drone in enumerate(drones):
            angle = math.tau * index / count - math.pi / 2
            dx = x + math.cos(angle) * ring_radius
            dy = y + math.sin(angle) * ring_radius

            self.canvas.create_oval(
                dx - 13, dy - 13,
                dx + 13, dy + 13,
                fill="#f8fafc",
                outline="#0f172a",
                width=2,
            )
            self.canvas.create_text(
                dx, dy,
                text=drone.name,
                fill="#0f172a",
                font=("Arial", 8, "bold"),
            )

    def _draw_drones(self) -> None:
        """Draw drones in zones or at connection midpoints."""
        groups: dict[
            tuple[float, float], list[DroneView]
        ] = defaultdict(list)

        for drone in self.frame.drones:
            if drone.zone is not None:
                position = self.positions[drone.zone]
            elif drone.connection is not None:
                start, end = drone.connection
                x1, y1 = self.positions[start]
                x2, y2 = self.positions[end]
                position = ((x1 + x2) / 2, (y1 + y2) / 2)
            else:
                continue

            groups[position].append(drone)

        for (x, y), drones in groups.items():
            self._draw_drone_group(drones, x, y)

    def _draw(self) -> None:
        """Render the complete current frame."""
        self.canvas.delete("all")
        self._calculate_positions()
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()

    def _update_status(self) -> None:
        """Update counters and disable controls on completion."""
        suffix = " — Finished" if self.frame.finished else ""
        self.status.set(
            f"Turn: {self.frame.turn} | "
            f"Delivered: {self.frame.delivered}{suffix}"
        )

        state = tk.DISABLED if self.frame.finished else tk.NORMAL
        self.next_button.configure(state=state)
        self.play_button.configure(state=state)

    def step(self) -> None:
        """Advance one turn and handle simulation errors."""
        if self.frame.finished:
            return

        try:
            self.frame = self.next_frame()
            self._draw()
            self._update_status()
        except Exception as error:
            self.pause()
            messagebox.showerror(
                "Simulation error",
                str(error),
                parent=self.root,
            )
            return

        if self.frame.finished:
            self.pause()

    def _tick(self) -> None:
        """Run one scheduled turn and schedule the next."""
        self.timer = None
        if not self.playing:
            return

        self.step()

        if self.playing:
            try:
                delay = max(50, self.delay.get())
            except tk.TclError:
                delay = 500

            self.timer = self.root.after(delay, self._tick)

    def toggle_play(self) -> None:
        """Start or pause automatic playback."""
        if self.playing:
            self.pause()
        elif not self.frame.finished:
            self.playing = True
            self.play_button.configure(text="Pause")
            self._tick()

    def pause(self) -> None:
        """Stop playback and cancel any pending callback."""
        self.playing = False
        self.play_button.configure(text="Play")

        if self.timer is not None:
            self.root.after_cancel(self.timer)
            self.timer = None

    def close(self) -> None:
        """Cancel playback and destroy the window."""
        self.pause()
        self.root.destroy()

    def run(self) -> None:
        """Start the graphical event loop."""
        self.root.mainloop()

    def restart(self) -> None:
        """Restart the simulation from its initial state."""
        self.pause()

        try:
            self.frame = self.restart_frame()
            self._draw()
            self._update_status()
        except Exception as error:
            messagebox.showerror(
                "Restart error",
                str(error),
                parent=self.root,
            )


class SimulationVisualizer:
    """Connect the simulation to the graphical interface."""

    def __init__(self, simulation: Simulation) -> None:
        """Build the visual representation of the simulation.

        Args:
            simulation: The simulation to display.
        """
        self.simulation = simulation
        graph = simulation.graph

        zones = [
            ZoneView(
                name=zone.name,
                x=zone.x,
                y=zone.y,
                color=zone.color,
                zone_type=zone.zone_type,
                capacity=(
                    None
                    if zone is graph.start_zone or zone is graph.end_zone
                    else zone.max_drones
                ),
            )
            for zone in graph.zones.values()
        ]

        connections = [
            ConnectionView(
                start=connection.zone_a.name,
                end=connection.zone_b.name,
                capacity=connection.max_link_capacity,
            )
            for connection in graph.connections
        ]

        self.visualizer = Visualizer(
            zones=zones,
            connections=connections,
            initial_frame=self.build_frame(),
            next_frame=self.next_frame,
            restart_frame=self.restart_frame,
        )

    def build_frame(self) -> Frame:
        """Convert the current simulation state into a display frame.

        Returns:
            The frame describing the current turn.

        Raises:
            ValueError: If a drone is neither in a zone nor on a connection.
        """
        drones: list[DroneView] = []

        for drone in self.simulation.drones:
            if drone.state == State.FINISHED:
                continue

            if drone.current_connection is not None:
                connection = drone.current_connection
                drones.append(
                    DroneView(
                        name=f"D{drone.id}",
                        connection=(
                            connection.zone_a.name,
                            connection.zone_b.name,
                        ),
                    )
                )
            elif drone.current_zone is not None:
                drones.append(
                    DroneView(
                        name=f"D{drone.id}",
                        zone=drone.current_zone.name,
                    )
                )
            else:
                raise ValueError(
                    f"Drone {drone.id} has no displayable position"
                )

        return Frame(
            turn=self.simulation.current_turn,
            drones=drones,
            delivered=self.simulation.finished_drones,
            finished=self.simulation.is_finished(),
        )

    def next_frame(self) -> Frame:
        """Execute one turn, print its movements, and return its state.

        Returns:
            The frame describing the new turn.
        """
        if not self.simulation.is_finished():
            self.simulation.step()
            print(" ".join(self.simulation.movement_history[-1]))

        return self.build_frame()

    def restart_frame(self) -> Frame:
        """Reset the simulation and return its initial frame."""
        self.simulation.reset()
        return self.build_frame()

    def run(self) -> None:
        """Open the graphical interface."""
        self.visualizer.run()
