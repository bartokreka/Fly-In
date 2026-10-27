from dataclasses import dataclass
from .ConnectionClass import Connection
from .DroneClass import Drone
from .ZoneClass import Zone

@dataclass
class Movement:
    drone: Drone
    destination: Zone
    connection: Connection
    is_arrival: bool = True

    def print_movement(self) -> None:

        print(self.drone.print())
        if self.destination is not None:
            print(self.destination.print())
        if self.connection is not None:
            print(self.connection.print_connection())