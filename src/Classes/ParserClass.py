from .GraphClass import Graph
from .DroneClass import Drone
from .ZoneClass import Zone
from .ConnectionClass import Connection


class Parser:
    def __init__(self, file: str) -> None:
        self._file = file

    ZONE_TYPES = {
        "normal",
        "restricted",
        "blocked",
        "priority"
    }

    VALID_KEYS = {
        "nb_drones",
        "start_hub",
        "end_hub",
        "hub",
        "connection"
    }

    VALID_ZONE_METADATA = {
        "zone",
        "color",
        "max_drones",
    }

    @classmethod
    def from_file(cls, filename: str) -> Graph:
        text = cls._parse_file(filename)
        graph = cls._build_graph(text)
        return graph

    @staticmethod
    def _parse_file(filename: str) -> list[tuple[int, str, str]]:
        entries: list[tuple[int, str, str]] = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line_nr, raw_line in enumerate(f, start=1):
                    line = raw_line.strip()

                    # Ignore empty lines, and commented out lines
                    if not line or line.startswith("#"):
                        continue
                    # Remove inline comments
                    if "#" in line:
                        line = line.split("#", 1)[0].strip()
                    if ":" not in line:
                        raise ValueError(f"Line {line_nr} missing ':' separator")  # noqa: E501
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Ignore unknown key value pairs
                    if key not in Parser.VALID_KEYS:
                        raise ValueError(f"{key} is not a valid data format")
                    if value == "":
                        raise ValueError(
                            f"Line {line_nr}: missing value for key '{key}'"
                        )
                    if not key:
                        raise ValueError(f"Line {line_nr}: empty key")
                    entries.append((line_nr, key, value))
        except ValueError as e:
            raise ValueError(str(e)) from e
        line_nr, key, value = entries[0]
        if key != "nb_drones":
            raise ValueError("The first line must define the number of drones using nb_drones: <positive_integer>")  # noqa: E501
        try:
            num = int(value)
        except ValueError:
            raise ValueError("Number of drones must be an integer")
        if num < 0:
            raise ValueError("Number of drones cannot be negative")
        return entries

    @staticmethod
    def _validate_metadata(data: str, type: str, is_start_or_end_hub: bool = False) -> list[tuple[str, str | int]]:  # noqa: E501
        metadata: list[tuple[str, str | int]] = []
        data = data.strip("[]")
        data = data.split(" ")
        for entries in data:
            try:
                key, value = entries.split("=")
            except ValueError:
                raise ValueError("Metadata should be given in [key = value] form")  # noqa: E501
            if type == "zone" and key not in Parser.VALID_ZONE_METADATA:
                raise ValueError(f"{key} not a valid metadata for a zone")
            if type == "connection" and key != "max_link_capacity":
                raise ValueError(f"{key} not a valid metadata for a connection")  # noqa: E501
            if key in ["max_drones", "max_link_capacity"] and not is_start_or_end_hub:  # noqa: E501
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(f"{value} is not a positive integer for {key} metadata")  # noqa: E501
                if value <= 0:
                    raise ValueError(f"{key} metadata must be a positive integer, and greater than 0")  # noqa: E501
            metadata.append((key, value))
        return metadata

    @staticmethod
    def extract_start_end(entries: list[tuple[int, str, str]]) -> tuple[Zone, Zone]:  # noqa: E501
        start_zone: Zone | None = None
        end_zone: Zone | None = None
        for line_nr, key, value in entries:
            if key == "start_hub":
                if start_zone is not None:
                    raise ValueError(f"Line {line_nr}: duplicate start_hub")
                zone_values = value.split(" ", 3)
                metadata = []
                try:
                    metadata = Parser._validate_metadata(zone_values[3], "zone", True)
                except ValueError as e:
                    print(e)
                    return
                if not Parser.is_valid_zone_name(zone_values[0]):
                    raise ValueError("Zone names can use any valid characters except dashes and spaces")  # noqa: E501
                start_zone = Zone(zone_values[0], int(zone_values[1]), int(zone_values[2]))  # noqa: E501
                for key, value in metadata:
                    if key == "color":
                        start_zone.color = value
                    if key == "zone":
                        start_zone.zone_type = value
                start_zone.max_drones = None
            if key == "end_hub":
                if end_zone is not None:
                    raise ValueError(f"Line {line_nr}: duplicate end_hub")
                zone_values = value.split(" ", 3)
                try:
                    metadata = Parser._validate_metadata(zone_values[3], "zone")
                except ValueError as e:
                    raise ValueError(f"Line {line_nr}: {e}") from e
                if not Parser.is_valid_zone_name(zone_values[0]):
                    raise ValueError("Zone names can use any valid characters except dashes and spaces")  # noqa: E501
                end_zone = Zone(zone_values[0], int(zone_values[1]), int(zone_values[2]))  # noqa: E501
                for key, value in metadata:
                    if key == "color":
                        end_zone.color = value
                    if key == "zone":
                        end_zone.zone_type = value
                end_zone.max_drones = None
        if start_zone is None or end_zone is None:
            raise ValueError("Missing start_hub or end_hub")
        return ([start_zone, end_zone])

    @classmethod
    def _build_graph(cls, entries: list[tuple[int, str, str]]) -> Graph:
        graph = Graph()
        start, end = cls.extract_start_end(entries)
        graph.start_zone = start
        graph.end_zone = end
        for line_nr, key, value in entries:
            if key == "nb_drones":
                drone_nr = int(value)
                for i in range(drone_nr):
                    drone = Drone(i+1, start)
                    graph.drones.append(drone)
            if key == "hub":
                zone = Parser._parse_zone(value)
                graph.add_zone(zone)
            # if key == "connection":
            #     connection = Parser._parse_connection(value, graph)
            #     graph.add_connection(connection)
        graph.print_graph()
        return graph

    @staticmethod
    def is_valid_zone_name(name: str) -> bool:
        """Check whether a zone name contains valid characters."""
        return bool(name) and "-" not in name and " " not in name

    @staticmethod
    def _parse_zone(value: str) -> Zone:
        zone_values = value.split(" ", 3)
        metadata = []
        try:
            metadata = Parser._validate_metadata(zone_values[3], False)
        except ValueError as e:
            print(e)
            return
        if not Parser.is_valid_zone_name(zone_values[0]):
            raise ValueError("Zone names can use any valid characters except dashes and spaces")  # noqa: E501
        zone = Zone(zone_values[0], int(zone_values[1]), int(zone_values[2]))  # noqa: E501
        for key, value in metadata:
            if key == "color":
                zone.color = value
            if key == "zone":
                zone.zone_type = value
            if key == "max_zones":
                zone.zone_type = value
        return zone

    @staticmethod
    def _parse_connection(value: str, graph: Graph) -> Connection:
        # connection: gate_hell4-gate_hell5 [max_link_capacity=1]
        value = value.split(" ", 1)
        zone_a_name, zone_b_name = value[0].split("-")
        for zone in graph.zones:
            if zone[0] == zone_a_name:
                zone_a = zone[1]
            if zone[0] == zone_b_name:
                zone_b = zone[1]
        if len(value) > 1:
            metadata = []
            try:
                metadata = Parser._validate_metadata(value[1], "connection", False)
            except ValueError as e:
                print(e)
                return
        if len(value) > 1:
            print(metadata)
        # connection = Connection(zone_a, zone_b, metadata)
