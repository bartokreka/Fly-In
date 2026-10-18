from .GraphClass import Graph
from .DroneClass import Drone
from .ZoneClass import Zone


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

    # @staticmethod
    # def extract_start_end(entries: list[tuple[int, str, str]]) -> list[Zone]:
    #     for line_nr, key, value in entries:
    #         if key == "start_hub":

    #             start_zone = Zone()
    
    @classmethod
    def _build_graph(cls, entries: list[tuple[int, str, str]]) -> Graph:
        graph = Graph()
        # start_zone = cls.extract_start_end(entries)[0]
        # end_zone = cls.extract_start_end(entries)[1]
        # for line_nr, key, value in entries:
        #     if key == "nb_drones":
        #         drone_nr = int(value)
        #         for i in range(drone_nr):
        #             drone = Drone(i+1)
        #             graph.drones.append(drone)
        print(entries)
        print(graph)
        return graph

    # @staticmethod
    # def _parse_zone(value: str) -> Zone:
    #     # Parse coordinates and metadata
    #     ...

    # @staticmethod
    # def _parse_connection(
    #     value: str,
    #     graph: Graph,
    # ) -> Connection:
    #     # Validate endpoints and capacity
    #     ...