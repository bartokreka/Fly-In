from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ConnectionClass import Connection


class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal", color: str = "none",
                 max_drones: int | None = 1) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.connections: list[Connection] = []
        self.is_end_zone: bool = False

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

    def get_cost(self) -> int:
        if self.zone_type == "normal" or self.zone_type == "priority":
            return 1
        elif self.zone_type == "blocked":
            return float("inf")
        elif self.zone_type == "restricted":
            return 2

    def get_neighbors(self) -> list[Zone]:
        neighbors: list[Zone] = []
        for connection in self.connections:
            if connection.zone_a == self:
                neighbors.append(connection.zone_b)
            elif connection.zone_b == self:
                neighbors.append(connection.zone_a)
        return neighbors

    def print(self) -> str:
        text = f"Zone {self.name} ({self.x}, {self.y}) with color {self.color}, max capacity of {self.max_drones} drones"  # noqa: E501
        if self.connections:
            text += (f"Connections to {self.connections}")
        print(text)
        return text
