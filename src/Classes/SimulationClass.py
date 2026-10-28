from .GraphClass import Graph
from .DroneClass import Drone, State
from .ZoneClass import Zone
from .SchedulerClass import Scheduler
from .MovementClass import Movement
from .RouteAllocatorClass import RouteAllocator
from .TerminalVisualizerClass import TerminalVisualizer


class Simulation:
    """Turn-by-turn simulation of drones flying from start to end.

    Attributes:
        graph: The drone network.
        drones: All drones in the simulation.
        current_turn: Number of completed turns.
        finished_drones: Number of drones that reached the end zone.
        movement_history: Formatted moves of each completed turn.
        solution_paths: Candidate paths the drones are assigned to.
    """

    def __init__(self, graph: Graph, paths: list[list[Zone]]) -> None:
        """Create the drones and assign each one a route.

        Args:
            graph: The drone network.
            paths: Candidate paths from the start zone to the end zone.

        Raises:
            ValueError: If the graph has no start or end zone, or if
                ``paths`` is empty.
        """
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
        self.solution_paths = paths
        allocator = RouteAllocator(self.solution_paths)
        allocator.assign_routes(self.drones)

    def run(self) -> None:
        """Run the simulation to completion, printing each turn's moves."""
        while not self.is_finished():
            self.step()
            print(" ".join(self.movement_history[-1]))
            # self.print_simulation()

    def execute_move(self, movement: Movement) -> str:
        """Apply a planned movement to its drone.

        Args:
            movement: The movement to apply.

        Returns:
            The move in output format, ``D<id>-<zone>`` or
            ``D<id>-<connection>``, colored with the destination color.

        Raises:
            ValueError: If a restricted move has no connection.
        """
        drone = movement.drone
        destination = movement.destination
        if movement.is_arrival:
            drone.arrive_to_zone(destination)
            text = f"D{drone.id}-{destination.name}"
        elif destination.zone_type == "restricted":
            if movement.connection is None:
                raise ValueError("Restricted movement needs a connection")
            drone.start_restricted_move(destination, movement.connection)
            text = f"D{drone.id}-{movement.connection.name}"
        else:
            drone.arrive_to_zone(destination)
            text = f"D{drone.id}-{destination.name}"
        visualizer = TerminalVisualizer()
        return str(visualizer.colorize(text, destination.color))

    def step(self) -> None:
        """Execute one simultaneous simulation turn.

        Raises:
            RuntimeError: If no drone can move while the simulation is not
                finished.
        """
        history: list[str] = []
        route_plan = Scheduler(self.graph).step_plan(self.drones)

        if not route_plan and not self.is_finished():
            raise RuntimeError("Simulation is stuck: no possible moves")
        for movement in route_plan:
            print_text = self.execute_move(movement)
            # movement.print_movement()
            history.append(print_text)
        finished = 0
        for drone in self.drones:
            if drone.state == State.FINISHED:
                finished += 1
        self.finished_drones = finished
        self.current_turn += 1
        self.movement_history.append(history)

    def is_finished(self) -> bool:
        """Check whether all drones have arrived.

        Returns:
            True if every drone reached the end zone.
        """
        return self.finished_drones == len(self.drones)

    def print_simulation(self) -> None:
        """Print the current simulation state for debugging."""
        print("\n========== SIMULATION ==========")
        print(f"Current turn: {self.current_turn}")
        print(f"\n{len(self.drones)} Drones:")
        for drone in self.drones:
            print(f"D{drone.id}, state: {drone.state.value}")
            print(f"Current zone: {drone.current_zone.name if drone.current_zone is not None else None}, target zone: {drone.target_zone.name if drone.target_zone is not None else None}")  # noqa: E501
            print(f"current index: {drone.route_index}")
        print(f"Finished drones: {self.finished_drones}")
        print("Movement history:")
        for turn, moves in enumerate(self.movement_history, start=1):
            print(f"Turn {turn}: {' '.join(moves)}")
        print("===========================\n")
