# Scheduler
#  └── Assigns drones and plans movements

from .DroneClass import Drone, State
from .ZoneClass import Zone
from .ConnectionClass import Connection
from .GraphClass import Graph


class Scheduler:
    def __init__(self, graph: Graph):
        self.graph = graph

    def get_zone_occupancy(self, drones: list[Drone]) -> dict[Zone, int]:  # noqa: E501
        zone_occupancy: dict[Zone, int] = {}
        for drone in drones:
            zone = drone.current_zone
            if zone is not None:
                zone_occupancy[zone] = zone_occupancy.get(zone, 0) + 1
        return zone_occupancy

    def get_connection_occupancy(self, drones: list[Drone]) -> dict[Connection, int]:  # noqa: E501
        connection_occupancy: dict[Connection, int] = {}
        for drone in drones:
            connection = drone.current_connection
            if connection is not None:
                connection_occupancy[connection] = connection_occupancy.get(connection, 0) + 1  # noqa: E501
        return connection_occupancy

    def modify_zone_occupancy(self, zone_occupancy: dict[Zone, int], zone: Zone, method: str) -> None:  # noqa: E501
        occupied = zone_occupancy.get(zone, 0)
        if method == "remove":
            if occupied <= 0:
                raise ValueError("Cannot remove from an empty zone")
            zone_occupancy[zone] = occupied - 1
        elif method == "add":
            zone_occupancy[zone] = occupied + 1
        else:
            raise ValueError(f"Unknown occupancy operation: {method}")

    def modify_connection_occupancy(self, connection_occupancy: dict[Connection, int], connection: Connection, method: str) -> None:  # noqa: E501
        occupied = connection_occupancy.get(connection, 0)
        if method == "remove":
            if occupied <= 0:
                raise ValueError("Cannot remove from an empty connection")
            connection_occupancy[connection] = occupied - 1
        elif method == "add":
            connection_occupancy[connection] = occupied + 1
        else:
            raise ValueError(f"Unknown occupancy operation: {method}")

    @staticmethod
    def is_zone_available(next_zone: Zone, zone_occupancy: dict[Zone, int]) -> bool:  # noqa: E501
        if next_zone.is_end_zone:
            return True
        occupied = zone_occupancy.get(next_zone, 0)
        return occupied < next_zone.max_drones

    @staticmethod
    def is_connection_available(connection: Connection, connection_occupancy: dict[Connection, int]) -> bool:  # noqa: E501
        occupied = connection_occupancy.get(connection, 0)
        return occupied < connection.max_link_capacity

    def step_plan(self, drones: list[Drone]) -> list[tuple[Drone, Zone]]:  # noqa: E501
        step_plan: list[tuple[Drone, Zone]] = []
        zone_occupancy = self.get_zone_occupancy(drones)
        connection_occupancy = self.get_connection_occupancy(drones)

        waiting_drones = []
        for drone in drones:
            if drone.state == State.WAITING:
                waiting_drones.append(drone)
        drone_reverse_list: list[Drone] = sorted(waiting_drones, key=lambda drone: drone.route_index, reverse=True)  # noqa: E501
        for drone in drone_reverse_list:
            start_zone = drone.current_zone
            if start_zone is None:
                raise ValueError(f"Waiting drone {drone.id} has no current zone")  # noqa: E501
            next_zone = drone.get_next_zone()
            if next_zone is None:
                raise ValueError(f"Waiting drone {drone.id} has no next zone")
            connection = self.graph.get_connection(start_zone, next_zone)
            if connection is None:
                raise ValueError(f"No connection for drone {drone.id}'s next move")  # noqa: E501
            if not self.is_zone_available(next_zone, zone_occupancy):
                continue
            if not self.is_connection_available(connection, connection_occupancy):  # noqa: E501
                continue
            step_plan.append([drone, next_zone])
            self.modify_zone_occupancy(zone_occupancy, start_zone, "remove")
            self.modify_zone_occupancy(zone_occupancy, next_zone, "add")
            self.modify_connection_occupancy(connection_occupancy, connection, "add")  # noqa: E501

        return step_plan
