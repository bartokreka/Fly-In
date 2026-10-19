from .ZoneClass import Zone


class Pathfinder:
    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        costs = {start: 0}
        previous: dict[Zone, Zone] = {}
        visited: set[Zone] = set()

        while True:
            # 1. Find the unvisited zone with the lowest cost
            current = None
            lowest_cost = float("inf")
            for zone in costs:
                if zone in visited:
                    continue
                if costs[zone] < lowest_cost:
                    lowest_cost = costs[zone]
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
                cost = neighbor.get_cost()
                if cost == float("inf"):
                    continue
                new_cost = costs[current] + cost
                if neighbor in costs:
                    old_cost = costs[neighbor]
                else:
                    old_cost = float("inf")
                # 4. update if new is cheaper
                if new_cost < old_cost:
                    costs[neighbor] = new_cost
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
    def print_path(path: list[Zone]):
        path_length = len(path)
        for i in range(path_length):
            print(path[i].name)
            if i + 1 < path_length:
                print(" | ")
