import argparse
from pathlib import Path
from typing import Any
from .Classes.ParserClass import Parser
from .Classes.AlgorithmClass import Pathfinder


def parse_arguments() -> Any:
    """Parse command-line arguments for the application.

    Returns:
        Parsed command-line arguments containing the map text file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, required=False)
    return parser.parse_args()


def main() -> None:
    """Run the drone simulation"""
    args = parse_arguments()
    map_path = args.map
    if not map_path:
        try:
            map_path = Path("/maps/easy/01_linear_path.txt")
        except ValueError:
            print("Error, no valid file for map found!")
            return
    try:
        graph = Parser.from_file(map_path)
    except ValueError as e:
        print(e)
        return
    start = graph.start_zone
    end = graph.end_zone
    # graph.print_graph()
    alg = Pathfinder()
    path = alg.find_path(start, end)
    if not path:
        return
    alg.print_path(path)


if __name__ == "__main__":
    main()
