from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ZoneClass import Zone


class Connection:
    def __init__(self, zone_a: "Zone", zone_b: "Zone",
                 max_link_capacity: int = 1,) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def get_other_zone(self, zone: "Zone") -> "Zone":
        if zone is self.zone_a:
            return self.zone_b
        if zone is self.zone_b:
            return self.zone_a
        raise ValueError("Zone is not part of the connection")

    def print(self) -> None:
        print(f"Connection between {self.zone_a} \
              and {self.zone_b} with max drone capacity \
                of {self.max_link_capacity}")
