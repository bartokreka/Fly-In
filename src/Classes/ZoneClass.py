from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ConnectionClass import Connection


class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal", color: str = "none",
                 max_drones: int = 1) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.connections: list[Connection] = []

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

    def print(self) -> None:
        print(f"Zone {self.name} ({self.x}, {self.y}) \
              with color {self.color}, max capacity of {self.max_drones} \
                drones, with connections to {self.connections}")
