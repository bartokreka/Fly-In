# Simulation
#  └── Executes turns and checks constraints
from .GraphClass import Graph

class Simulation:
    def __init__(self, graph: Graph, drone_count:int) -> None:
        self.graph = graph
        self.turns = 0

