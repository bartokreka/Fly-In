from .ZoneClass import Zone


class Pathfinder:
    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        costs = {start: 0}
        priority_counts = {start: 0}
        previous: dict[Zone, Zone] = {}
        visited: set[Zone] = set()

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
                print("There is no possible solution for this graph!")
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

    @staticmethod
    def print_path(path: list[Zone]) -> None:
        path_length = len(path)
        for i in range(path_length):
            print(path[i].name)
            if i + 1 < path_length:
                print(" | ")
