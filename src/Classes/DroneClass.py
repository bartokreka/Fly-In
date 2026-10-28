from enum import Enum
from .ZoneClass import Zone
from .ConnectionClass import Connection


class State(str, Enum):
    """Lifecycle states of a drone.

    Attributes:
        WAITING: The drone is parked in a zone, ready to move.
        MOVING: The drone is in transit on a connection toward a
            restricted zone.
        FINISHED: The drone has reached the end zone.
    """

    WAITING = "waiting"
    MOVING = "moving"
    FINISHED = "finished"


class Drone:
    """A drone travelling from the start zone to the end zone.

    Attributes:
        id: Drone number, starting at 1.
        state: Current lifecycle state.
        current_zone: Zone the drone is in, or None while in transit.
        current_connection: Connection the drone is travelling on, or None
            when it is in a zone.
        target_zone: Restricted zone the drone is moving into, or None.
        route: Zones the drone follows from start to end.
        route_index: Index in ``route`` of the last zone reached.
    """

    def __init__(self, id: int, start_zone: Zone):
        """Initialize a waiting drone in the start zone.

        Args:
            id: Drone number, starting at 1.
            start_zone: Zone the drone starts in.
        """
        self.id = id
        self.state = State.WAITING
        self.current_zone: Zone | None = start_zone
        self.current_connection: Connection | None = None
        self.target_zone: Zone | None = None
        self.route: list[Zone] | None = None
        self.route_index: int = 0

    def arrive_to_zone(self, zone: Zone) -> None:
        """Place the drone in a zone and advance it along its route.

        Clears any in-transit data and marks the drone as finished if the
        zone is the end zone, otherwise as waiting.

        Args:
            zone: The zone the drone arrives in.
        """
        self.current_zone = zone
        self.current_connection = None
        self.target_zone = None
        self.route_index += 1
        if zone.is_end_zone:
            self.state = State.FINISHED
        else:
            self.state = State.WAITING

    def start_restricted_move(self, target_zone: Zone, connection: Connection) -> None:  # noqa: E501
        """Put the drone in transit toward a restricted zone.

        Entering a restricted zone takes two turns. During the first turn
        the drone occupies the connection instead of a zone.

        Args:
            target_zone: The restricted zone being entered.
            connection: The connection the drone travels on.
        """
        self.current_zone = None
        self.current_connection = connection
        self.target_zone = target_zone
        self.state = State.MOVING

    def get_next_zone(self) -> Zone | None:
        """Return the next zone on the drone's route.

        Returns:
            The next zone on the route, or None if the drone is not waiting,
            has no route, or has already reached the end of its route.
        """
        if self.state != State.WAITING:
            return None
        if not self.route:
            return None
        next_route_index = self.route_index + 1
        if len(self.route) <= next_route_index:
            return None
        return self.route[next_route_index]

    def print(self) -> str:
        """Build a short human-readable description of the drone.

        Returns:
            A string with the drone id and its current state.
        """
        return (f"Drone {self.id} with state {self.state}")
