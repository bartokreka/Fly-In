from .DroneClass import Drone
from .ZoneClass import Zone


class RouteAllocator:
    """Distribute drones across candidate paths.

    Attributes:
        paths: Candidate paths from the start zone to the end zone.
    """

    def __init__(self, paths: list[list[Zone]]) -> None:
        """Initialize the allocator with candidate paths.

        Args:
            paths: Candidate paths from the start zone to the end zone.

        Raises:
            ValueError: If ``paths`` is empty.
        """
        if not paths:
            raise ValueError("No available paths")
        self.paths = paths

    def get_path_cost(self, path: list[Zone]) -> int:
        """Compute the total travel cost of a path.

        The first zone is excluded, since drones are already there.

        Args:
            path: Ordered zones from start to end.

        Returns:
            The sum of the costs of every zone after the first.
        """
        sum = 0
        for zone in path[1:]:
            sum += zone.get_cost()
        return sum

    def assign_routes(self, drones: list[Drone]) -> None:
        """Assign a route to each drone, balancing the load across paths.

        Each drone gets the path with the lowest cost plus number of drones
        already assigned to it. Ties go to the cheaper path.

        Args:
            drones: Drones to assign routes to. Their ``route`` attribute is
                updated in place.
        """
        assigned = [0] * len(self.paths)
        for drone in drones:
            best_index = min(
                range(len(self.paths)),
                key=lambda i: (
                    self.get_path_cost(self.paths[i])
                    + assigned[i],
                    self.get_path_cost(self.paths[i])
                )
            )
            drone.route = self.paths[best_index]
            assigned[best_index] += 1
            # print([zone.name for zone in drone.route])
