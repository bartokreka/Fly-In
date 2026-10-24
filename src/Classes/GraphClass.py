from .ZoneClass import Zone
from .ConnectionClass import Connection
from .DroneClass import Drone


class Graph:
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.drone_count: int = 0
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone: {zone.name}")
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
        connection.zone_a.add_connection(connection)
        connection.zone_b.add_connection(connection)

    def get_connection(self, start_zone: Zone, end_zone: Zone) -> Connection | None:  # noqa: E501
        if not start_zone or not end_zone:
            return None
        for connection in self.connections:
            if connection.zone_a == start_zone and connection.zone_b == end_zone:  # noqa: E501
                return connection
        return None

    def print_graph(self) -> None:
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

        print("\nStart zone:",
            self.start_zone.name if self.start_zone else "None")
        print("End zone:",
            self.end_zone.name if self.end_zone else "None")

        print("===========================\n")
