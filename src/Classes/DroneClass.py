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
        if zone.is_end_zone:
            self.state = State.FINISHED
        else:
            self.state = State.WAITING

    def start_resticted_move(self, target_zone: Zone, connection: Connection) -> None:
        self.current_zone = None
        self.current_connection = connection
        self.target_zone = target_zone
        self.state = State.MOVING

    def print(self) -> None:
        print(f"Drone {self.id} with state {self.state}, start zone: {self.start_zone.print()}")  # noqa: E501