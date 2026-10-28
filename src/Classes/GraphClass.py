from .ZoneClass import Zone
from .ConnectionClass import Connection


class Graph:
    """The drone network described by a map file.

    Attributes:
        zones: Zones indexed by name.
        connections: All connections between zones.
        drone_count: Number of drones to route from start to end.
        start_zone: Zone where all drones start.
        end_zone: Zone all drones must reach.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.drone_count: int = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone: {zone.name}")
        self.zones[zone.name] = zone

    def special_max_drone_update(self, zone: Zone) -> None:
        """Remove the capacity limit of a zone.

        Used for the start and end hubs, which can hold any number of
        drones.

        Args:
            zone: The zone to make unlimited. Must already be in the graph.
        """
        self.zones[zone.name].max_drones = None

    def add_connection(self, connection: Connection) -> None:
        """Add a connection and register it on both of its endpoint zones.

        Args:
            connection: The connection to add.
        """
        self.connections.append(connection)
        connection.zone_a.add_connection(connection)
        connection.zone_b.add_connection(connection)

    def get_connection(self, start_zone: Zone, end_zone: Zone) -> Connection | None:  # noqa: E501
        """Find the connection between two zones, in either direction.

        Args:
            start_zone: One endpoint of the connection.
            end_zone: The other endpoint of the connection.

        Returns:
            The connection linking both zones, or None if they are not
            directly connected.
        """
        if not start_zone or not end_zone:
            return None
        for connection in self.connections:
            if connection.zone_a == start_zone and connection.zone_b == end_zone:  # noqa: E501
                return connection
            elif connection.zone_b == start_zone and connection.zone_a == end_zone:  # noqa: E501
                return connection
        return None

    def print_graph(self) -> None:
        """Print the zones, connections and hubs for debugging."""
        print("\n========== GRAPH ==========")

        print(f"\nZones ({len(self.zones)}):")
        for zone in self.zones.values():
            print(f"  {vars(zone)}")

        print(f"\nConnections ({len(self.connections)}):")
        for connection in self.connections:
            print(
                f"  {connection.zone_a.name} <-> "
                f"{connection.zone_b.name}"
            )
            print(f"    {vars(connection)}")

        print(f"\nDrones ({self.drone_count}):")

        print("\nStart zone:", self.start_zone.name if self.start_zone else "None")  # noqa: E501
        print("End zone:", self.end_zone.name if self.end_zone else "None")  # noqa: E501

        print("===========================\n")
