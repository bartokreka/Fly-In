from .DroneClass import Drone
from .ZoneClass import Zone


class RouteAllocator:
    def __init__(self, paths: list[list[Zone]]) -> None:
        if not paths:
            raise ValueError("No available paths")
        self.paths = paths

    def get_path_cost(self, path: list[Zone]) -> int:
        sum = 0
        for zone in path[1:]:
            sum += zone.get_cost()
        return sum

    def assign_routes(self, drones: list[Drone]) -> None:
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
