# Simulation
#  └── Executes turns and checks constraints
from .GraphClass import Graph
from .DroneClass import Drone, State
from .ZoneClass import Zone
from .SchedulerClass import Scheduler
from .TerminalVisualizerClass import TerminalVisualizer


class Simulation:
    def __init__(self, graph: Graph, path: list[Zone]) -> None:
        if graph.start_zone is None or graph.end_zone is None:
            raise ValueError("Graph must have start and end zones")
        self.graph = graph
        self.drones: list[Drone] = [
            Drone(i + 1, graph.start_zone)
            for i in range(graph.drone_count)
        ]
        self.current_turn: int = 0
        self.finished_drones: int = 0
        self.movement_history: list[list[str]] = []
        # temporary manual setup
        self.solution_path = path

    def update_drone_paths(self) -> None:
        for drone in self.drones:
            drone.route = self.solution_path

    def run(self) -> None:
        # temporary manual setup
        self.update_drone_paths()
        while not self.is_finished():
            self.step()
            print(" ".join(self.movement_history[-1]))

    def step(self) -> None:
        """Execute one simultaneous simulation turn."""
        history: list[str] = []
        route_plan = Scheduler(self.graph).step_plan(self.drones)
        visualizer : TerminalVisualizer = TerminalVisualizer()
        if not route_plan and not self.is_finished():
            raise RuntimeError("Simulation is stuck: no possible moves")
        for drone, zone in route_plan:
            drone.arrive_to_zone(zone)
            text = f"D{drone.id}-{zone.name}"
            colored_text = visualizer.colorize(text, zone.color)
            history.append(colored_text)
        finished = 0
        for drone in self.drones:
            if drone.state == State.FINISHED:
                finished += 1
        self.finished_drones = finished
        self.current_turn += 1
        self.movement_history.append(history)

    def is_finished(self) -> bool:
        """Check whether all drones have arrived."""
        return self.finished_drones == len(self.drones)

    def print_simulation(self) -> None:
        print("\n========== SIMULATION ==========")
        print(f"Current turn: {self.current_turn}")
        print(f"\n{len(self.drones)} Drones:")
        for drone in self.drones:
            print(f"D{drone.id}, state: {drone.state.value}")
            print(f"Current zone: {drone.current_zone.name if drone.current_zone is not None else None}, target zone: {drone.target_zone.name if drone.target_zone is not None else None}")
            print(f"current index: {drone.route_index}")
        print(f"Finished drones: {self.finished_drones}")
        print("Movement history:")
        for turn, moves in enumerate(self.movement_history, start=1):
            print(f"Turn {turn}: {' '.join(moves)}")
        print("===========================\n")
