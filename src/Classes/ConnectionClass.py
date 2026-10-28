from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ZoneClass import Zone


class Connection:
    """A bidirectional link between two zones.

    Attributes:
        name: Connection identifier, as written in the map file.
        zone_a: First endpoint of the connection.
        zone_b: Second endpoint of the connection.
        max_link_capacity: Maximum number of drones allowed in transit on
            the connection at the same time.
    """

    def __init__(self, name: str, zone_a: "Zone", zone_b: "Zone", max_link_capacity: int = 1,) -> None:  # noqa: E501
        """Initialize a connection.

        Args:
            name: Connection identifier, as written in the map file.
            zone_a: First endpoint of the connection.
            zone_b: Second endpoint of the connection.
            max_link_capacity: Maximum number of drones allowed in transit
                on the connection at the same time.
        """
        self.name = name
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def get_other_zone(self, zone: "Zone") -> "Zone":
        """Return the endpoint opposite to the given zone.

        Args:
            zone: One endpoint of this connection.

        Returns:
            The other endpoint of this connection.

        Raises:
            ValueError: If ``zone`` is not an endpoint of this connection.
        """
        if zone is self.zone_a:
            return self.zone_b
        if zone is self.zone_b:
            return self.zone_a
        raise ValueError("Zone is not part of the connection")

    def print_connection(self) -> str:
        """Build a human-readable description of the connection.

        Returns:
            A string describing both endpoints and the link capacity.
        """
        return (f"Connection between {self.zone_a} and {self.zone_b} with max drone capacity of {self.max_link_capacity}")  # noqa: E501
