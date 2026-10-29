*This project has been created as part of the 42 curriculum by rbartok*

# FLY-IN

## Description

Fly-in is a multi-agent drone routing simulation. A map file describes a
network of zones (hubs) linked by connections, plus a number of drones that all
start in the same start hub. The goal is to fly every drone to the end hub in
as few simulation turns as possible, while respecting the rules of the
network:

- **Zone capacity**: a zone holds at most `max_drones` drones at once
  (default 1). The start and end hubs are unlimited.
- **Link capacity**: a connection carries at most `max_link_capacity` drones
  in the same turn (default 1).
- **Zone types**:
  - `normal`: entering takes 1 turn.
  - `priority`: entering takes 1 turn, and these zones are preferred when
    paths have the same cost.
  - `restricted`: entering takes 2 turns. The drone spends the first turn on
    the connection.
  - `blocked`: these zones can never be entered.

The program parses and validates the map, computes several candidate paths,
spreads the drones across them, and then simulates the flight turn by turn.
Each turn's moves are printed to the terminal, and the network can be watched
in a graphical window.

### Project structure

```
fly-in/
├── Makefile
├── pyproject.toml
├── maps/                         # easy, medium, hard, challenger and custom maps
└── src/
    ├── __main__.py               # entry point: parse → find paths → simulate → display
    └── Classes/
        ├── ParserClass.py        # reads and validates map files, builds the Graph
        ├── GraphClass.py         # zones, connections, start/end hubs, drone count
        ├── ZoneClass.py          # a hub: position, type, color, capacity, cost
        ├── ConnectionClass.py    # a bidirectional link with a capacity
        ├── AlgorithmClass.py     # Pathfinder: Dijkstra + Yen's k-shortest paths
        ├── RouteAllocatorClass.py      # assigns one path to each drone
        ├── DroneClass.py         # drone state machine (waiting / moving / finished)
        ├── MovementClass.py      # one planned move in a turn
        ├── SchedulerClass.py     # decides which drones may move in a turn
        ├── SimulationClass.py    # runs the turns and records the move history
        ├── TerminalVisualizerClass.py  # colored terminal output
        └── VisualizerClass.py    # Tkinter graphical interface
```

The `Graph` handles the network, and the `Simulation` handles the drones and
their movement.

## Instructions

### Requirements

- Python 3.10 or newer, with Tkinter (included with most Python installs;
  on Linux you may need the `python3-tk` package)
- [uv](https://docs.astral.sh/uv/)

To check if Tkinter works in your environment run the following command (That should open a small test window.):
```
uv run python -c "import tkinter; tkinter._test()"
```

### Installation

```bash
make install        # uv sync: creates .venv and installs the dev tools
```

### Running

```bash
uv run python -m src --map maps/easy/02_simple_fork.txt
```

`make run` runs the map selected in the [Makefile](Makefile). The other maps are
listed there as comments, so uncomment the one you want.

### Other targets

| Command      | Description                                          |
|--------------|------------------------------------------------------|
| `make lint`  | Runs `flake8` and `mypy` in strict mode               |
| `make debug` | Runs the program under `pdb` on a custom map         |
| `make clean` | Removes `__pycache__` and `.mypy_cache` directories   |

### Map file format

```
# Comments start with '#'
nb_drones: 4                                   # must be the first entry, > 0

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: slow 2 -1 [zone=restricted color=red]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-slow
connection: slow-goal
```

- Each line is `key: value`. The valid keys are `nb_drones`, `start_hub`,
  `end_hub`, `hub` and `connection`.
- Hubs are written as `name x y [metadata]`. Names cannot contain dashes or
  spaces. Coordinates are integers.
- Hub metadata can include `zone=<type>`, `color=<name>` and
  `max_drones=<n>`.
- Connections are written as `zoneA-zoneB [max_link_capacity=<n>]`. Both
  zones must already be defined, and the same connection cannot appear twice.
- Any invalid input makes the program stop with an error message that gives
  the line number.

## Resources

- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Video explaining Dijkstra's algorithm](https://www.youtube.com/watch?v=bZkzH5x0SKU)
- [Yen's k-shortest paths algorithm](https://en.wikipedia.org/wiki/Yen%27s_algorithm)
- [Multi-agent pathfinding](https://en.wikipedia.org/wiki/Multi-agent_pathfinding)
- [Tkinter documentation](https://docs.python.org/3/library/tkinter.html)

### Use of AI

AI (Claude) was used to write the docstrings and to draft this README from the
source code.
I also used chatGPT to help me understand conceptual problems and possible architectural solutions on how to build my classes and a roadmap on how to build the project step by step, always adding more complexity to an already working simple or sometimes manual solutions. The VisualizerClass was written by GPT, reviewed and changed by me.

## Algorithm choices and implementation strategy

The problem is split into four stages.

### 1. Parsing (`Parser`)

The map is read line by line. Comments are stripped, and every key, value and
metadata entry is validated. The result is a `Graph` that holds `Zone` and
`Connection` objects. The start and end hubs are created first, so their
capacity can be set to unlimited.

### 2. Path finding (`Pathfinder`)

- **Cost model**: moving into a `normal` or `priority` zone costs 1 and moving
  into a `restricted` zone costs 2. `blocked` zones are never expanded, so
  dead ends and forbidden zones are skipped automatically.
- **Dijkstra (`find_path`)** finds the cheapest path. When two paths cost the
  same, the one that crosses more `priority` zones wins.
- **Yen's algorithm (`find_paths`)** finds up to 5 distinct loopless paths,
  ordered from best to worst. Having several paths lets drones avoid
  bottlenecks instead of queueing on one corridor. Each new path is built by
  branching off a previous path at a "spur" node, while excluding the zones
  and connections already used by the shared root.

### 3. Route allocation (`RouteAllocator`)

Drones are assigned one at a time to the path that minimises
`path cost + number of drones already on that path`. The cheaper path breaks
ties. This greedy balance sends drones down a slightly longer path once the
best one is crowded enough that queueing would cost more than the detour.

### 4. Turn scheduling (`Scheduler`, `Simulation`)

Each turn, the scheduler builds a list of moves that are all applied at once:

1. **Arrivals are mandatory.** Drones that are in transit toward a restricted
   zone always complete their move first, which frees the link and reserves
   their spot in the zone.
2. **Waiting drones are planned from the front of the queue.** Drones are
   sorted by how far they are along their route, most advanced first, so space
   is freed ahead before the drones behind try to move into it.
3. **Capacity checks.** A drone only moves if its next zone has room (the end
   hub is unlimited) and the connection is below its capacity. Occupancy
   counts are updated as each move is planned.
4. **Restricted zones.** Entering one takes two turns, so the scheduler checks
   whether the zone will have room *next* turn. It counts drones already
   reserved to arrive, and it subtracts the drones that are guaranteed to
   leave toward the end hub (capped by that link's capacity). This lets
   drones keep flowing through restricted zones that sit next to the goal.
5. Drones that cannot move wait. If no drone can move but the simulation is
   not finished, a `RuntimeError` reports that it is stuck.

Routes are fixed at the start. Drones wait instead of being rerouted, which
keeps the scheduler simple and predictable.

## Visual representation

### Terminal

Each turn is printed on one line as a list of moves:

- `D<id>-<zone>`: the drone moved into a zone.
- `D<id>-<zoneA>-<zoneB>`: the drone is in transit on a connection toward a
  restricted zone.

Each move is colored with the destination zone's color, using ANSI codes.
Drones that do not move in a turn are not listed.

### Graphical window (Tkinter)

- **Zones** are large circles in their map color, positioned from the map
  coordinates and scaled to fit the window. Each label shows the name, type
  and `occupancy / capacity`.
- **Connections** are lines labelled with their link capacity.
- **Drones** are small white circles labelled `D<id>`. Drones that share a
  zone are arranged in a ring. Drones in transit to a restricted zone are
  drawn at the middle of the connection. Delivered drones disappear.
- **Controls**: *Next turn* steps one turn, *Play/Pause* animates the turns,
  and the delay field sets the speed (50–3000 ms, default 500 ms). The status
  bar shows the current turn and the number of delivered drones.

## Example inputs and outputs

### Simple fork (`maps/easy/02_simple_fork.txt`)

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction D4-junction
D1-goal D2-goal D3-path_a D4-path_b
D3-goal D4-goal
```

Four turns: the drones split between both branches, and the junction is
refilled as soon as it is emptied.

### Restricted zone (`maps/custom/1_linear_restricted.txt`)

```
nb_drones: 1

start_hub: start 0 0 [color=green]
hub: zone 1 0 [zone=restricted color=blue]
end_hub: goal 3 0 [color=red]

connection: start-zone
connection: zone-goal
```

```
D1-start-zone
D1-zone
D1-goal
```

Entering the restricted zone takes two turns. In the first turn the drone is
on the `start-zone` connection.

### Results on the provided maps

| Map                                       | Drones | Turns |  Optimal |
|-------------------------------------------|-------:|------:|---------:|
| easy/01_linear_path                       |      2 |     4 |        4 |
| easy/02_simple_fork                       |      4 |     4 |        4 |
| easy/03_basic_capacity                    |      4 |     4 |        4 |
| medium/01_dead_end_trap                   |      5 |     8 |        8 |
| medium/02_circular_loop                   |      6 |    11 |       10 |
| medium/03_priority_puzzle                 |      5 |     7 |        6 |
| hard/01_maze_nightmare                    |      8 |    13 |       13 |
| hard/02_capacity_hell                     |     12 |    16 |       16 |
| hard/03_ultimate_challenge                |     15 |    28 |       26 |
| challenger/01_the_impossible_dream        |     25 |    48 |       43 |
| custom/1_linear_restricted                |      1 |     3 |        3 |
| custom/1_linear_restricted_stress         |      2 |     4 |        4 |
