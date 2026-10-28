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
        cost: int = 1
        if self.zone_type == "normal" or self.zone_type == "priority":
            return cost
        elif self.zone_type == "blocked":
            cost = -1
        elif self.zone_type == "restricted":
            cost = 2
        return cost

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
        if self.is_end_zone:
            text += "\nIT'S THE END\n"
        if self.connections:
            text += (f"Connections to {self.connections}")
        return text
