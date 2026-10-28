# Scheduler
#  └── Assigns drones and plans movements

from .DroneClass import Drone, State
from .ZoneClass import Zone
from .ConnectionClass import Connection
from .GraphClass import Graph
from .MovementClass import Movement


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
        if next_zone.max_drones is None:
            return True
        occupied = zone_occupancy.get(next_zone, 0)
        return occupied < next_zone.max_drones

    @staticmethod
    def is_connection_available(connection: Connection, connection_occupancy: dict[Connection, int]) -> bool:  # noqa: E501
        occupied = connection_occupancy.get(connection, 0)
        return occupied < connection.max_link_capacity

    @staticmethod
    def get_required_arrivals(drones: list[Drone]) -> list[tuple[Drone, Zone]]:
        arrivals = []
        for drone in drones:
            if drone.state == State.MOVING:
                if drone.target_zone is None:
                    raise ValueError("Moving drone has no target")
                arrivals.append((drone, drone.target_zone))
        return arrivals

    @staticmethod
    def can_start_restricted(zone: Zone, occupancy: dict[Zone, int], reservations: dict[Zone, int], guaranteed_departures: dict[Zone, int], is_end: bool = False) -> bool:  # noqa: E501
        if is_end:
            return True
        capacity = zone.max_drones
        if capacity is None:
            return True
        occupied = occupancy.get(zone, 0)
        reserved = reservations.get(zone, 0)
        departures = guaranteed_departures.get(zone, 0)
        return occupied - departures + reserved < capacity

    def get_guaranteed_departures(self, zone: Zone, planned_drones: list[Drone]) -> int:  # noqa: E501
        if self.graph.end_zone is None:
            return 0
        connection = self.graph.get_connection(zone, self.graph.end_zone)
        if connection is None:
            return 0
        eligible = 0
        for drone in planned_drones:
            if drone.route is None:
                continue
            if drone.state == State.MOVING:
                # The drone will arrive at zone this turn.
                # Its next move is one position further.
                next_index = drone.route_index + 2
            else:
                next_index = drone.route_index + 1
            if next_index >= len(drone.route):
                continue

            if drone.route[next_index] is self.graph.end_zone:
                eligible += 1
        return min(eligible, connection.max_link_capacity)

    def step_plan(self, drones: list[Drone]) -> list[Movement]:  # noqa: E501
        step_plan: list[Movement] = []
        zone_occupancy = self.get_zone_occupancy(drones)
        connection_occupancy = self.get_connection_occupancy(drones)
        moving_drones: list[Drone] = []
        waiting_drones: list[Drone] = []
        reservations: dict[Zone, int] = {}
        for drone in drones:
            if drone.state == State.WAITING:
                waiting_drones.append(drone)
            elif drone.state == State.MOVING:
                moving_drones.append(drone)
        # Mandatory restricted arrivals
        for drone in moving_drones:
            if drone.target_zone is None:
                raise ValueError("Moving drone has no target")
            if drone.current_connection is None:
                raise ValueError("Moving drone has no connection")
            destination = drone.target_zone
            step_plan.append(Movement(drone, destination, drone.current_connection, is_arrival=True))
            self.modify_connection_occupancy(connection_occupancy, drone.current_connection, "remove")
            self.modify_zone_occupancy(zone_occupancy, destination, "add")
        # Plan waiting drones
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
            if next_zone.zone_type == "blocked":
                continue
            if next_zone.zone_type == "restricted":
                # Find drones that will occupy this zone
                # at the end of the current turn.
                planned_drones = [
                    other
                    for other in waiting_drones
                    if other.current_zone is next_zone
                    and not any(
                        move.drone is other
                        for move in step_plan
                    )
                ]

                planned_drones.extend(
                    other
                    for other in moving_drones
                    if other.target_zone is next_zone
                )

                departures = self.get_guaranteed_departures(
                    next_zone,
                    planned_drones
                )

                guaranteed_departures = {
                    next_zone: departures
                }
                if not self.can_start_restricted(next_zone, zone_occupancy, reservations, guaranteed_departures, next_zone == self.graph.end_zone):
                    continue
            else:
                if (
                    next_zone is not self.graph.end_zone
                    and not self.is_zone_available(
                        next_zone,
                        zone_occupancy
                    )
                ):
                    continue
            if not self.is_connection_available(connection, connection_occupancy):  # noqa: E501
                continue
            step_plan.append(Movement(drone, next_zone, connection, is_arrival=False))  # noqa: E501
            self.modify_zone_occupancy(zone_occupancy, start_zone, "remove")
            if next_zone.zone_type == "restricted":
                reservations[next_zone] = reservations.get(next_zone, 0) + 1
            else:
                self.modify_zone_occupancy(zone_occupancy, next_zone, "add")
            self.modify_connection_occupancy(connection_occupancy, connection, "add")  # noqa: E501

        return step_plan
