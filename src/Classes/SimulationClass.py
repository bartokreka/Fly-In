# Simulation
#  └── Executes turns and checks constraints
from .GraphClass import Graph
from .DroneClass import Drone


class Simulation:
    def __init__(self, graph: Graph) -> None:
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

    def run(self) -> None:
        while not self.is_finished():
            self.step()

    def step(self) -> None:
        """Execute one simultaneous simulation turn."""
        pass

    def is_finished(self) -> bool:
        """Check whether all drones have arrived."""
        return self.finished_drones == len(self.drones)

    # apply_movements()	Apply all approved movements simultaneously
    # record_turn()	Store movements for output

    def print_simulation(self) -> None:
        print("\n========== SIMULATION ==========")
        print(f"Current turn: {self.current_turn}")
        print(f"\nDrones ({len(self.drones)}):")
        for drone in self.drones:
            print(f"  {vars(drone)}")
        print(f"Finished drones: {self.finished_drones}")
        print("Movement history:")
        for turn, moves in enumerate(self.movement_history, start=1):
            print(f"Turn {turn}: {' '.join(moves)}")
        print("===========================\n")
