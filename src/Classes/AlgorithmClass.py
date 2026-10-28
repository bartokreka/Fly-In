from .ZoneClass import Zone


# mypy: disable-error-code="assignment"
class Pathfinder:
    """Find cheapest paths through the zone graph.

    Paths are ranked by total zone cost. Among paths of equal cost, the
    one crossing more priority zones is preferred.
    """

    def find_path(self, start: Zone, end: Zone, excluded_zones: set[Zone] | None = None, excluded_edges: set[frozenset[Zone]] | None = None) -> list[Zone]:  # noqa: E501
        """Find the cheapest path between two zones with Dijkstra's algorithm.

        Blocked zones are never entered. Ties in cost are broken in favor of
        the path visiting more priority zones.

        Args:
            start: Zone the path starts from.
            end: Zone the path must reach.
            excluded_zones: Zones the path must not pass through.
            excluded_edges: Connections, given as unordered zone pairs, the
                path must not use.

        Returns:
            The zones from ``start`` to ``end`` inclusive, or an empty list
            if ``end`` cannot be reached.
        """
        costs = {start: 0}
        priority_counts = {start: 0}
        previous: dict[Zone, Zone] = {}
        visited: set[Zone] = set()
        excluded_zones = excluded_zones or set()
        excluded_edges = excluded_edges or set()

        while True:
            # 1. Find the unvisited zone with the lowest cost
            current = None
            lowest_cost = float("inf")
            highest_priority_count = -1
            for zone in costs:
                if zone in visited:
                    continue
                if costs[zone] < lowest_cost:
                    lowest_cost = costs[zone]
                    highest_priority_count = priority_counts[zone]
                    current = zone
                elif costs[zone] == lowest_cost:
                    if priority_counts[zone] > highest_priority_count:
                        highest_priority_count = priority_counts[zone]
                        current = zone
            if current is None:
                return []
            if current == end:
                break
            # 2. Mark the current zone as visited
            visited.add(current)
            # 3. Explore all neighbors
            neighbors = current.get_neighbors()
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                if neighbor in excluded_zones:
                    continue
                edge = frozenset((current, neighbor))
                if edge in excluded_edges:
                    continue
                cost = neighbor.get_cost()
                if cost < 1:
                    continue
                new_cost = costs[current] + cost
                new_priority_count = priority_counts[current]
                if neighbor.zone_type == "priority":
                    new_priority_count += 1
                if neighbor in costs:
                    old_cost = costs[neighbor]
                else:
                    old_cost = float("inf")
                if neighbor in priority_counts:
                    old_priority_count = priority_counts[neighbor]
                else:
                    old_priority_count = 0
                # priority compare
                should_update = False
                if new_cost < old_cost:
                    should_update = True

                elif new_cost == old_cost:
                    if new_priority_count > old_priority_count:
                        should_update = True
                # 4. update if new is cheaper or has more priority
                if should_update:
                    costs[neighbor] = new_cost
                    priority_counts[neighbor] = new_priority_count
                    previous[neighbor] = current
        # 5. reconstruct path
        path = []
        current = end
        while current != start:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()
        return path

    def get_path_cost(self, path: list[Zone]) -> int:
        """Compute the total travel cost of a path.

        The first zone is excluded, since drones are already there.

        Args:
            path: Ordered zones from start to end.

        Returns:
            The sum of the costs of every zone after the first.
        """
        sum = 0
        for zone in path[1:]:
            sum += zone.get_cost()
        return sum

    def get_priority_count(self, path: list[Zone]) -> int:
        """Count the priority zones on a path, excluding the first zone.

        Args:
            path: Ordered zones from start to end.

        Returns:
            The number of priority zones after the first zone.
        """
        prio_sum = 0
        for zone in path[1:]:
            if zone.zone_type == "priority":
                prio_sum += 1
        return prio_sum

    def find_paths(self, start: Zone, end: Zone, k: int = 5) -> list[list[Zone]]:  # noqa: E501
        """Find up to ``k`` distinct cheapest paths with Yen's algorithm.

        Args:
            start: Zone the paths start from.
            end: Zone the paths must reach.
            k: Maximum number of paths to return.

        Returns:
            Loopless paths ordered from best to worst. Fewer than ``k`` paths
            are returned if not enough exist, and none if ``end`` cannot be
            reached or ``k`` is not positive.
        """
        if k <= 0:
            return []
        first_path = self.find_path(start, end)
        if not first_path:
            return []
        paths: list[list[Zone]] = [first_path]
        candidates: list[list[Zone]] = []
        while len(paths) < k:
            previous_path = paths[-1]

            for i in range(len(previous_path) - 1):
                spur_node = previous_path[i]
                root_path = previous_path[:i + 1]

                excluded_edges: set[frozenset[Zone]] = set()

                for path in paths:
                    if (
                        len(path) > i + 1
                        and path[:i + 1] == root_path
                    ):
                        excluded_edges.add(
                            frozenset((path[i], path[i + 1]))
                        )

                excluded_zones = set(root_path[:-1])

                spur_path = self.find_path(
                    spur_node,
                    end,
                    excluded_zones=excluded_zones,
                    excluded_edges=excluded_edges
                )

                if not spur_path:
                    continue

                total_path = root_path[:-1] + spur_path

                if (
                    total_path not in paths
                    and total_path not in candidates
                ):
                    candidates.append(total_path)

            if not candidates:
                break

            candidates.sort(
                key=lambda path: (
                    self.get_path_cost(path),
                    -self.get_priority_count(path)
                )
            )

            best_path = candidates.pop(0)
            paths.append(best_path)
        return paths

    @staticmethod
    def print_path(path: list[Zone]) -> None:
        """Print the zone names of a path, one per line.

        Args:
            path: Ordered zones to print.
        """
        path_length = len(path)
        for i in range(path_length):
            print(path[i].name)
            if i + 1 < path_length:
                print(" | ")
