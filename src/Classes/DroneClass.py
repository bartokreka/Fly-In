from enum import Enum
from .ZoneClass import Zone


class State(str, Enum):
    START = "start"
    MOVING = "moving"
    WAITING = "waiting"
    FINISHED = "finished"


class Drone:
    def __init__(self, id: int, start_zone: Zone):
        self.id = id
        self.start_zone = start_zone
        self.state = State.START

    def print(self) -> None:
        print(f"Drone {self.id} with state {self.state}, start zone: {self.start_zone.print()}")  # noqa: E501