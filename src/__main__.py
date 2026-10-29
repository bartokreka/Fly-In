import argparse
import tkinter as tk
from pathlib import Path
from typing import Any
from .Classes.ParserClass import Parser
from .Classes.AlgorithmClass import Pathfinder
from .Classes.SimulationClass import Simulation
from .Classes.VisualizerClass import SimulationVisualizer


def parse_arguments() -> Any:
    """Parse command-line arguments for the application.

    Returns:
        Parsed command-line arguments containing the map text file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, required=False)
    return parser.parse_args()


def main() -> None:
    """Run the drone simulation.

    Parses the map, finds candidate paths and opens the graphical
    visualizer. Errors are printed instead of raised.
    """
    args = parse_arguments()
    map_path = args.map
    if not map_path:
        try:
            map_path = Path("maps/easy/01_linear_path.txt")
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
    paths = alg.find_paths(start, end, 5)
    # for path in paths:
    #     print([zone.name for zone in path])
    if len(paths) < 1:
        return
    # alg.print_path(path)
    simulation = Simulation(graph, paths)
    # simulation.run()
    try:
        visualization = SimulationVisualizer(simulation)
    except tk.TclError as error:
        print(f"Cannot open graphical window: {error}")
    else:
        visualization.run()


if __name__ == "__main__":
    main()
