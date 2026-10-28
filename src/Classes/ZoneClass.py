from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ConnectionClass import Connection


class Zone:
    """A zone of the drone network.

    Attributes:
        name: Unique zone name.
        x: Horizontal map coordinate.
        y: Vertical map coordinate.
        zone_type: One of ``normal``, ``priority``, ``restricted`` or
            ``blocked``.
        color: Display color name.
        max_drones: Maximum number of drones in the zone at once, or None
            for unlimited capacity.
        connections: Connections attached to the zone.
        is_end_zone: True if this is the zone drones must reach.
    """

    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal", color: str = "none",
                 max_drones: int | None = 1) -> None:
        """Initialize a zone.

        Args:
            name: Unique zone name.
            x: Horizontal map coordinate.
            y: Vertical map coordinate.
            zone_type: One of ``normal``, ``priority``, ``restricted`` or
                ``blocked``.
            color: Display color name.
            max_drones: Maximum number of drones in the zone at once, or
                None for unlimited capacity.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
        self.connections: list[Connection] = []
        self.is_end_zone: bool = False

    def add_connection(self, connection: Connection) -> None:
        """Register a connection attached to this zone.

        Args:
            connection: The connection to register.
        """
        self.connections.append(connection)

    def get_cost(self) -> int:
        """Return the cost of moving into this zone.

        Returns:
            1 for normal and priority zones, 2 for restricted zones and -1
            for blocked zones, which cannot be entered.
        """
        cost: int = 1
        if self.zone_type == "normal" or self.zone_type == "priority":
            return cost
        elif self.zone_type == "blocked":
            cost = -1
        elif self.zone_type == "restricted":
            cost = 2
        return cost

    def get_neighbors(self) -> list[Zone]:
        """Return the zones directly connected to this zone.

        Returns:
            The zone at the other end of each attached connection.
        """
        neighbors: list[Zone] = []
        for connection in self.connections:
            if connection.zone_a == self:
                neighbors.append(connection.zone_b)
            elif connection.zone_b == self:
                neighbors.append(connection.zone_a)
        return neighbors

    def print(self) -> str:
        """Build a human-readable description of the zone.

        Returns:
            A string with the zone position, color, capacity and
            connections.
        """
        text = f"Zone {self.name} ({self.x}, {self.y}) with color {self.color}, max capacity of {self.max_drones} drones"  # noqa: E501
        if self.is_end_zone:
            text += "\nIT'S THE END\n"
        if self.connections:
            text += (f"Connections to {self.connections}")
        return text
