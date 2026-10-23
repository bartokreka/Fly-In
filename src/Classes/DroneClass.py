from enum import Enum
from .ZoneClass import Zone
from .ConnectionClass import Connection


class State(str, Enum):
    WAITING = "waiting"
    MOVING = "moving"
    FINISHED = "finished"


class Drone:
    def __init__(self, id: int, start_zone: Zone):
        self.id = id
        self.state = State.WAITING
        self.current_zone: Zone | None = start_zone
        self.current_connection: Connection | None = None
        self.target_zone: Zone | None = None
        self.route: list[Zone] | None = None
        self.route_index: int = 0

    def arrive_to_zone(self, zone: Zone) -> None:
        self.current_zone = zone
        self.current_connection = None
        self.target_zone = None
        self.route_index += 1
        if zone.is_end_zone:
            self.state = State.FINISHED
        else:
            self.state = State.WAITING

    def start_restricted_move(self, target_zone: Zone, connection: Connection) -> None:
        self.current_zone = None
        self.current_connection = connection
        self.target_zone = target_zone
        self.state = State.MOVING

    def get_next_zone(self) -> Zone:
        next_zone = None
        if self.current_zone.is_end_zone:
            self.state = State.FINISHED
        else:
            next_zone = self.route[self.route_index]
        return next_zone

    def print(self) -> None:
        print(f"Drone {self.id} with state {self.state}, start zone: {self.current_zone.print()}")  # noqa: E501