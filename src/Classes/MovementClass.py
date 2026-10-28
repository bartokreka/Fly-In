from dataclasses import dataclass
from .ConnectionClass import Connection
from .DroneClass import Drone
from .ZoneClass import Zone


@dataclass
class Movement:
    """A single drone move planned for a simulation turn.

    Attributes:
        drone: The drone that moves.
        destination: The zone the drone moves toward.
        connection: The connection used for the move.
        is_arrival: True if the drone completes a restricted move started
            in the previous turn, False if it starts a new move.
    """

    drone: Drone
    destination: Zone
    connection: Connection
    is_arrival: bool = True

    def print_movement(self) -> None:
        """Print the drone, destination and connection for debugging."""
        print(self.drone.print())
        if self.destination is not None:
            print(self.destination.print())
        if self.connection is not None:
            print(self.connection.print_connection())
