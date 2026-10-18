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