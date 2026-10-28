from .GraphClass import Graph
from .ZoneClass import Zone
from .ConnectionClass import Connection


# mypy: disable-error-code="assignment"
class Parser:
    """Parse map files into a graph.

    Attributes:
        ZONE_TYPES: Allowed values for the ``zone`` metadata.
        VALID_KEYS: Allowed line keys in a map file.
        VALID_ZONE_METADATA: Allowed metadata keys for a hub.
    """

    def __init__(self, file: str) -> None:
        """Initialize a parser for a map file.

        Args:
            file: Path to the map file.
        """
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
        """Parse a map file and build its graph.

        Args:
            filename: Path to the map file.

        Returns:
            The graph described by the file.

        Raises:
            ValueError: If the file cannot be read or is malformed.
        """
        text = cls._parse_file(filename)
        graph = cls._build_graph(text)
        return graph

    @staticmethod
    def _parse_file(filename: str) -> list[tuple[int, str, str]]:
        """Read a map file into validated key-value entries.

        Comments, starting with ``#``, and blank lines are skipped.

        Args:
            filename: Path to the map file.

        Returns:
            A list of ``(line_number, key, value)`` tuples.

        Raises:
            ValueError: If the file cannot be read, is empty, contains an
                invalid line, or does not start with a single positive
                integer ``nb_drones`` entry.
        """
        entries: list[tuple[int, str, str]] = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line_nr, raw_line in enumerate(f, start=1):
                    line = raw_line.split("#", 1)[0].strip()
                    if not line:
                        continue
                    if ":" not in line:
                        raise ValueError(f"Line {line_nr} missing ':' separator")  # noqa: E501
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Ignore unknown key value pairs
                    if key not in Parser.VALID_KEYS:
                        raise ValueError(f"{key} is not a valid data format")
                    if not value:
                        raise ValueError(
                            f"Line {line_nr}: missing value for key '{key}'"
                        )
                    entries.append((line_nr, key, value))
        except OSError as e:
            raise ValueError(f"Cannot read file: {e}") from e
        if not entries:
            raise ValueError("Input file is empty")
        if entries[0][1] != "nb_drones":
            raise ValueError("First entry must be nb_drones")
        if sum(key == "nb_drones" for _, key, _ in entries) != 1:
            raise ValueError("Exactly one nb_drones entry is required")
        try:
            num = int(entries[0][2])
        except ValueError as e:
            raise ValueError("Number of drones must be an integer") from e
        if num <= 0:
            raise ValueError("Number of drones must be positive")
        return entries

    @staticmethod
    def _validate_metadata(data: str, type: str, is_start_or_end_hub: bool = False) -> list[tuple[str, str | int]]:  # noqa: E501
        """Parse and validate a bracketed metadata string.

        Args:
            data: Metadata such as ``[zone=restricted color=red]``.
            type: Either ``"zone"`` or ``"connection"``, selecting which keys
                are allowed.
            is_start_or_end_hub: If True, ``max_drones`` is neither converted
                nor checked, since hubs have unlimited capacity.

        Returns:
            A list of ``(key, value)`` pairs. Capacity values are converted
            to integers.

        Raises:
            ValueError: If the format is invalid, a key or value is not
                allowed, a key is duplicated, or a capacity is not a
                positive integer.
        """
        metadata: list[tuple[str, str | int]] = []
        if not data.startswith("[") or not data.endswith("]"):
            raise ValueError("Metadata must have the following format: [metadata]")  # noqa: E501
        data = data.strip("[]")
        if not data:
            raise ValueError("Metadata cannot be empty")
        data = data.split(" ")
        for entries in data:
            try:
                key, value = entries.split("=")
            except ValueError as e:
                raise ValueError("Metadata should be given in [key = value] form") from e  # noqa: E501
            if not key or not value:
                raise ValueError("Metadata key and value cannot be empty")
            if type == "zone" and key not in Parser.VALID_ZONE_METADATA:
                raise ValueError(f"{key} not a valid metadata for a zone")
            if type == "zone" and key == "zone" and value not in Parser.ZONE_TYPES:  # noqa: E501
                raise ValueError(f"{value} is not a valid zone type")
            if type == "connection" and key != "max_link_capacity":
                raise ValueError(f"{key} not a valid metadata for a connection")  # noqa: E501
            if any(existing == key for existing, _ in metadata):
                raise ValueError(f"Duplicate metadata: {key}")
            if key in ("max_drones", "max_link_capacity"):
                if not (key == "max_drones" and is_start_or_end_hub):
                    try:
                        value = int(value)
                    except ValueError as e:
                        raise ValueError(f"{value} is not a positive integer for {key} metadata") from e  # noqa: E501
                    if int(value) <= 0:
                        raise ValueError(f"{key} metadata must be greater than 0")  # noqa: E501
            metadata.append((key, value))
        return metadata

    @staticmethod
    def extract_start_end(entries: list[tuple[int, str, str]]) -> tuple[Zone, Zone]:  # noqa: E501
        """Create the start and end zones from the parsed entries.

        Args:
            entries: Parsed ``(line_number, key, value)`` tuples.

        Returns:
            A ``(start_zone, end_zone)`` tuple. Both zones have unlimited
            capacity and the end zone is flagged with ``is_end_zone``.

        Raises:
            ValueError: If a hub is missing, duplicated or malformed.
        """
        start_zone: Zone | None = None
        end_zone: Zone | None = None
        for line_nr, key, value in entries:
            if key not in ("start_hub", "end_hub"):
                continue
            if key == "start_hub" and start_zone is not None:
                raise ValueError(f"Line {line_nr}: duplicate start_hub")
            if key == "end_hub" and end_zone is not None:
                raise ValueError(f"Line {line_nr}: duplicate end_hub")
            try:
                zone_values = value.split(" ", 3)
                if len(zone_values) < 3:
                    raise ValueError("Missing zone name or coordinates")
                name = zone_values[0]
                if not Parser.is_valid_zone_name(name):
                    raise ValueError("Invalid zone name")
                x = int(zone_values[1])
                y = int(zone_values[2])
                metadata = []
                if len(zone_values) == 4:
                    metadata = Parser._validate_metadata(zone_values[3], "zone", True)  # noqa: E501
                zone = Zone(name, x, y)
                for meta_key, meta_value in metadata:
                    if meta_key == "color":
                        zone.color = meta_value
                    elif meta_key == "zone":
                        zone.zone_type = meta_value
                zone.max_drones = None
                if key == "start_hub":
                    start_zone = zone
                else:
                    end_zone = zone
                    end_zone.is_end_zone = True
            except ValueError as e:
                raise ValueError(f"Line {line_nr}: {e}") from e

        if start_zone is None or end_zone is None:
            raise ValueError("Missing start_hub or end_hub")

        return start_zone, end_zone

    @classmethod
    def _build_graph(cls, entries: list[tuple[int, str, str]]) -> Graph:
        """Build a graph from parsed entries.

        Args:
            entries: Parsed ``(line_number, key, value)`` tuples.

        Returns:
            The graph containing every zone and connection.

        Raises:
            ValueError: If an entry is invalid. The message includes its
                line number.
        """
        graph = Graph()
        start, end = cls.extract_start_end(entries)
        for line_nr, key, value in entries:
            try:
                if key == "nb_drones":
                    drone_nr = int(value)
                    graph.drone_count = drone_nr
                elif key == "start_hub":
                    graph.start_zone = start
                    graph.start_zone.max_drones = None
                    graph.add_zone(start)
                    graph.special_max_drone_update(start)
                elif key == "end_hub":
                    graph.end_zone = end
                    graph.end_zone.max_drones = None
                    graph.add_zone(end)
                    graph.special_max_drone_update(end)
                elif key == "hub":
                    zone = Parser._parse_zone(value)
                    graph.add_zone(zone)
                elif key == "connection":
                    connection = Parser._parse_connection(value, graph)
                    graph.add_connection(connection)
            except ValueError as e:
                raise ValueError(f"Line {line_nr}: {e}") from e
        return graph

    @staticmethod
    def is_valid_zone_name(name: str) -> bool:
        """Check whether a zone name contains valid characters.

        Args:
            name: The zone name to check.

        Returns:
            True if the name is not empty and contains no dash or space.
        """
        return bool(name) and "-" not in name and " " not in name

    @staticmethod
    def _parse_zone(value: str) -> Zone:
        """Create a zone from a ``hub`` entry value.

        Args:
            value: Text such as ``name x y [metadata]``.

        Returns:
            The zone described by the value.

        Raises:
            ValueError: If the name, coordinates or metadata are invalid.
        """
        zone_values = value.split(" ", 3)
        if len(zone_values) < 3:
            raise ValueError("Missing zone name or coordinates")
        if not Parser.is_valid_zone_name(zone_values[0]):
            raise ValueError("Invalid zone name")
        try:
            x = int(zone_values[1])
            y = int(zone_values[2])
        except ValueError as e:
            raise ValueError("Zone coordinates must be integers") from e
        metadata = []
        if len(zone_values) == 4:
            metadata = Parser._validate_metadata(zone_values[3], "zone")
        zone = Zone(zone_values[0], x, y)
        for key, value in metadata:
            if key == "color":
                zone.color = value
            elif key == "zone":
                zone.zone_type = value
            elif key == "max_drones":
                zone.max_drones = value
        return zone

    @staticmethod
    def _parse_connection(value: str, graph: Graph) -> Connection:
        """Create a connection from a ``connection`` entry value.

        Args:
            value: Text such as ``a-b [max_link_capacity=2]``.
            graph: The graph holding the zones defined so far.

        Returns:
            The connection described by the value.

        Raises:
            ValueError: If the format or metadata is invalid, a zone is
                undefined, or the connection already exists.
        """
        parts = value.split(maxsplit=1)
        names = parts[0].split("-")
        if len(names) != 2 or not all(names):
            raise ValueError("Invalid connection format")
        zone_a_name, zone_b_name = names
        zone_a = graph.zones.get(zone_a_name)
        zone_b = graph.zones.get(zone_b_name)
        if zone_a is None or zone_b is None:
            raise ValueError("Connection references an undefined zone")
        for existing in graph.connections:
            if {existing.zone_a.name, existing.zone_b.name} == {
                zone_a_name, zone_b_name
            }:
                raise ValueError("Duplicate connection")
        connection = Connection(parts[0], zone_a, zone_b)
        if len(parts) > 1:
            metadata = Parser._validate_metadata(parts[1], "connection")
            for key, value in metadata:
                if key == "max_link_capacity":
                    connection.max_link_capacity = value
        return connection
