from .DroneClass import Drone, State
from .ZoneClass import Zone
from .ConnectionClass import Connection
from .GraphClass import Graph
from .MovementClass import Movement


class Scheduler:
    """Plan which drones move during a simulation turn.

    Zone and connection capacities are respected. A drone may start
    moving into a full restricted zone if enough drones are guaranteed
    to leave it toward the end zone.

    Attributes:
        graph: The drone network.
    """

    def __init__(self, graph: Graph):
        """Initialize the scheduler.

        Args:
            graph: The drone network.
        """
        self.graph = graph

    def get_zone_occupancy(self, drones: list[Drone]) -> dict[Zone, int]:  # noqa: E501
        """Count the drones currently in each zone.

        Args:
            drones: All drones in the simulation.

        Returns:
            The number of drones in each occupied zone. Drones in transit
            are not counted.
        """
        zone_occupancy: dict[Zone, int] = {}
        for drone in drones:
            zone = drone.current_zone
            if zone is not None:
                zone_occupancy[zone] = zone_occupancy.get(zone, 0) + 1
        return zone_occupancy

    def get_connection_occupancy(self, drones: list[Drone]) -> dict[Connection, int]:  # noqa: E501
        """Count the drones currently in transit on each connection.

        Args:
            drones: All drones in the simulation.

        Returns:
            The number of drones on each occupied connection.
        """
        connection_occupancy: dict[Connection, int] = {}
        for drone in drones:
            connection = drone.current_connection
            if connection is not None:
                connection_occupancy[connection] = connection_occupancy.get(connection, 0) + 1  # noqa: E501
        return connection_occupancy

    def modify_zone_occupancy(self, zone_occupancy: dict[Zone, int], zone: Zone, method: str) -> None:  # noqa: E501
        """Add or remove one drone from a zone's occupancy count.

        Args:
            zone_occupancy: Drone count per zone, updated in place.
            zone: The zone to update.
            method: Either ``"add"`` or ``"remove"``.

        Raises:
            ValueError: If removing from an empty zone or if ``method`` is
                unknown.
        """
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
        """Add or remove one drone from a connection's occupancy count.

        Args:
            connection_occupancy: Drone count per connection, updated in
                place.
            connection: The connection to update.
            method: Either ``"add"`` or ``"remove"``.

        Raises:
            ValueError: If removing from an empty connection or if
                ``method`` is unknown.
        """
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
        """Check whether a zone has room for one more drone.

        Args:
            next_zone: The zone to enter.
            zone_occupancy: Drone count per zone.

        Returns:
            True if the zone is unlimited or below its capacity.
        """
        if next_zone.max_drones is None:
            return True
        occupied = zone_occupancy.get(next_zone, 0)
        return bool(occupied < next_zone.max_drones)

    @staticmethod
    def is_connection_available(connection: Connection, connection_occupancy: dict[Connection, int]) -> bool:  # noqa: E501
        """Check whether a connection has room for one more drone.

        Args:
            connection: The connection to use.
            connection_occupancy: Drone count per connection.

        Returns:
            True if the connection is below its capacity.
        """
        occupied = connection_occupancy.get(connection, 0)
        return bool(occupied < connection.max_link_capacity)

    @staticmethod
    def get_required_arrivals(drones: list[Drone]) -> list[tuple[Drone, Zone]]:
        """List the drones that must complete a restricted move this turn.

        Args:
            drones: All drones in the simulation.

        Returns:
            A ``(drone, target_zone)`` pair for every moving drone.

        Raises:
            ValueError: If a moving drone has no target zone.
        """
        arrivals = []
        for drone in drones:
            if drone.state == State.MOVING:
                if drone.target_zone is None:
                    raise ValueError("Moving drone has no target")
                arrivals.append((drone, drone.target_zone))
        return arrivals

    @staticmethod
    def can_start_restricted(zone: Zone, occupancy: dict[Zone, int], reservations: dict[Zone, int], guaranteed_departures: dict[Zone, int], is_end: bool = False) -> bool:  # noqa: E501
        """Check whether a drone may start moving into a restricted zone.

        The zone must have room when the drone arrives next turn, taking
        into account drones already heading there and drones guaranteed to
        leave it.

        Args:
            zone: The restricted zone to enter.
            occupancy: Drone count per zone.
            reservations: Drones already heading into each zone this turn.
            guaranteed_departures: Drones certain to leave each zone next
                turn.
            is_end: True if the zone is the end zone, which is unlimited.

        Returns:
            True if the move can start.
        """
        if is_end:
            return True
        capacity = zone.max_drones
        if capacity is None:
            return True
        occupied = occupancy.get(zone, 0)
        reserved = reservations.get(zone, 0)
        departures = guaranteed_departures.get(zone, 0)
        return bool(occupied - departures + reserved < capacity)

    def get_guaranteed_departures(self, zone: Zone, planned_drones: list[Drone]) -> int:  # noqa: E501
        """Count the drones certain to leave a zone toward the end zone.

        Args:
            zone: The zone to check.
            planned_drones: Drones that will be in the zone at the end of
                this turn.

        Returns:
            The number of drones whose next move is into the end zone,
            capped by the capacity of the connection to it. 0 if the zone is
            not directly connected to the end zone.
        """
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
        return int(min(eligible, connection.max_link_capacity))

    def step_plan(self, drones: list[Drone]) -> list[Movement]:  # noqa: E501
        """Plan all movements for the next turn.

        Drones in transit always complete their restricted move first.
        Waiting drones are then planned, the most advanced along their route
        first, and only move if the next zone and connection have room.

        Args:
            drones: All drones in the simulation.

        Returns:
            The movements to execute this turn.

        Raises:
            ValueError: If a drone is in an inconsistent state or its route
                uses a missing connection.
        """
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
            step_plan.append(Movement(drone, destination, drone.current_connection, is_arrival=True))  # noqa: E501
            self.modify_connection_occupancy(connection_occupancy, drone.current_connection, "remove")  # noqa: E501
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
                if not self.can_start_restricted(next_zone, zone_occupancy, reservations, guaranteed_departures, next_zone == self.graph.end_zone):  # noqa: E501
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
