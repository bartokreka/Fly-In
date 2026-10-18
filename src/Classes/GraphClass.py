from .ZoneClass import Zone
from .ConnectionClass import Connection
from .DroneClass import Drone


class Graph:
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone: {zone.name}")
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(self.connection)
        connection.zone_a.add_connection(connection)
        connection.zone_b.add_connection(connection)
