
import random
from time import sleep
from copy import deepcopy
from pyswip import Prolog

MAP_X, MAP_Y = 7, 6
REL_MAP_X = REL_MAP_Y = 13
REL_OFFSET_X = REL_OFFSET_Y = 6
GAME_MODE_NOTE = """
==================================================================================================================================
Note: Correctness of Localisation and Sensory Mapping is checked after every action.
Due to the nature of Agent's explore/1, for correctness of reposition/1 and reborn/0 please use [1] to control the agent manually.
In addition, the game will terminate under any of the following conditions:
1. Invalid localisation.
2. Invalid sensory mapping (wumpus, portal, coin, wall).
3. Explore/1 leads to unsafe cell.
==================================================================================================================================\n"""


class Map(object):
    DOT = "."
    CONFOUNDED = "%"  # Symbol 1
    STENCH = "="  # Symbol 2
    TINGLE = "T"  # Symbol 3
    NO_NPC = " "  # Symbol 4 & 6
    NPC = "-"    # Symbol 4 & 6
    NORTH = "^"  # Symbol 5 Agent North
    SOUTH = "v"  # Symbol 5 Agent South
    EAST = ">"  # Symbol 5 Agent East
    WEST = "<"  # Symbol 5 Agent West
    WUMPUS = "W"  # Symbol 5 Wumpus
    PORTAL = "O"  # Symbol 5 Portal
    UNSAFE = "U"  # Symbol 5 Wumpus / Portal
    VISITED = "S"  # Symbol 5 Visited
    UNVISITED = "s"  # Symbol 5 Unvisited Safe
    UNKNOWN = "?"  # Symbol 5 Unknown
    GLITTER = "*"  # Symbol 7
    BUMP = "B"  # Symbol 8
    SCREAM = "@"  # Symbol 9
    WALL = "#"  # Symbol Wall
    direction_symbol = {0: NORTH, 90: EAST, 180: SOUTH, 270: WEST}


class Item(object):
    WALL = "wall"
    COIN = "coin"
    AGENT = "agent"
    WUMPUS = "wumpus"
    PORTAL = "portal"


class Moveset(object):
    shoot = "shoot"
    pick_up = "pickup"
    turn_left = "turnleft"
    turn_right = "turnright"
    move_forward = "moveforward"
    options = {shoot, pick_up, turn_left, turn_right, move_forward}


class Agent(object):
    def __init__(self, prolog_file_name: str) -> None:
        self.prolog = Prolog()
        self.prolog.consult(prolog_file_name)  # Wait for Muq.

    def reborn(self) -> bool:
        return bool(list(self.prolog.query("reborn()", maxresult=10)))

    def move(self, action: str, sensor: list) -> bool:
        # sensor = str(sensor).replace("'", '')
        return bool(list(self.prolog.query(f"move({action},{sensor})", maxresult=10)))

    def reposition(self, L: list) -> bool:
        return bool(list(self.prolog.query(f"reposition({L})", maxresult=10)))

    def visited(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"visited({X},{Y})")))

    def wumpus(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"wumpus({X},{Y})")))

    def confundus(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"confundus({X},{Y})")))

    def tingle(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"tingle({X},{Y})")))

    def glitter(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"glitter({X},{Y})")))

    def stench(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"stench({X},{Y})")))

    def safe(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"safe({X},{Y})")))

    def explore(self, X: int, Y: int) -> bool:
        return self.prolog.query(f"explore({X},{Y})")

    def current(self, X: int, Y: int, D: int) -> bool:
        return bool(list(self.prolog.query(f"current({X},{Y},{D})")))

    def hasarrow(self) -> bool:
        return bool(list(self.prolog.query("hasarrow()"))) 

    def wall(self, X: int, Y: int) -> bool:
        return bool(list(self.prolog.query(f"wall({X},{Y})")))

    def query(self, s: str):
        return self.prolog.query(s)


class Driver(object):
    def __init__(self, file_name: str = "agent2.pl") -> None:
        # Initalise agent.
        self.agent = Agent(file_name)

        # Maps
        self.abs_map = self.rel_map = None

        # Initial Coordinates
        self.rel_boundary = (5, 7)
        self.origin_coord = (0, 0)
        self.abs_x = self.abs_y = self.abs_orient = 0
        self.rel_x = self.rel_y = self.rel_orient = 0

        # Game Variable
        self.has_arrow = False
        self.entered_portal = False
        self.safe_cells = [(x, y) for y in range(1, MAP_Y - 1)
                           for x in range(1, MAP_X - 1)]
        random.shuffle(self.safe_cells)

        # Stashed NPC Coordinates
        self.master_coords_item = {}
        self.master_item_coords = {Item.AGENT: None, Item.WUMPUS: None,
                                   Item.COIN: [], Item.PORTAL: [], Item.WALL: []}
        # NPC Coordinates
        self.coords_item = None
        self.item_coords = None

        # Build Boundary Walls.
        for x in range(MAP_X):
            for y in range(MAP_Y):
                if (x != 0 and x != MAP_X - 1) and (y != 0 and y != MAP_Y - 1):
                    continue
                self.master_item_coords[Item.WALL].append((x, y))
                self.master_coords_item[(x, y)] = Item.WALL

    # Manually input items.
    def recv_manual_item_input(self) -> None:
        # List of options.
        options = {"1": Item.AGENT, "2": Item.WUMPUS,
                   "3": Item.COIN, "4": Item.WALL, "5": Item.PORTAL, "6": "Done"}
        while True:
            # Screen 2.
            print("\n+=================================================+")
            print("+ [1] - Add agent.                                +")
            print("+ [2] - Add wumpus.                               +")
            print("+ [3] - Add coin.                                 +")
            print("+ [4] - Add wall.                                 +")
            print("+ [5] - Add confundus portal.                     +")
            print("+ [6] - Done.                                     +")
            print("+=================================================+")

            selected = input(f"[Input] Please enter your option: ")

            # Not a valid option.
            if selected not in options:
                print("[Error] Please enter a valid option (1 - 6).")
                continue

            cur_item = options[selected]

            # Done -> Check if Wumpus and Agent is added.
            if cur_item == "Done":
                if self.master_item_coords[Item.WUMPUS] is None:
                    print("[Screen] There must be at least one wumpus in the map.")
                    continue
                elif self.master_item_coords[Item.AGENT] is None:
                    print("[Screen] There must be one agent in the map.")
                    continue
                break

            if cur_item == Item.WUMPUS and self.master_item_coords[Item.WUMPUS] is not None:
                print("[Info] There can only be one wumpus on the map.")
                continue
            elif cur_item == Item.AGENT and self.master_item_coords[Item.AGENT] is not None:
                print("[Info] There can only be one agent on the map.")
                continue

            # Accept inputs from user.
            print(f"[Screen] Taking in {cur_item} (Enter -1 to stop).")

            while True:
                # Item's x and y coordinates.
                item_x = input(f"[Input] Enter {cur_item}'s x coord: ")
                item_y = input(f"[Input] Enter {cur_item}'s y coord: ")

                if item_x == "-1" or item_y == "-1":
                    break

                if not self.check_valid_coord(item_x, item_y):
                    print(f"[Error] ({item_x}, {item_y}) is out of bound.")
                    continue

                # Convert to (x, y) tuple.
                item_coord = (int(item_x), int(item_y))
                if item_coord not in self.master_coords_item:
                    print(f"[Screen] {cur_item} is added to {item_coord}.")
                    # Add to Item Dict and Coord Dict.
                    self.safe_cells.remove(item_coord)
                    self.master_coords_item[item_coord] = cur_item
                    if cur_item != Item.WUMPUS and cur_item != Item.AGENT:
                        self.master_item_coords[cur_item].append(item_coord)
                    else:
                        self.master_item_coords[cur_item] = item_coord
                        break
                else:
                    print(
                        f"[Screen] {item_coord} is already occupied by {self.master_coords_item[item_coord]}.")

    # Automatic Generate Inputs.
    def generate_item_input(self) -> None:
        # At least 1 coin, 1 wumpus, 3 portal, x walls.
        # Add in Wumpus.
        wumpus_coord = self.pop_safe_cell()
        self.master_item_coords[Item.WUMPUS] = wumpus_coord
        self.master_coords_item[wumpus_coord] = Item.WUMPUS

        # Other Items
        items = {Item.COIN: 1, Item.PORTAL: 3, Item.WALL: 0}

        for item_type, min_items in items.items():
            for _ in range(random.randint(min_items, max(min_items, (MAP_X * MAP_Y) // 14))):
                safe_coord = self.pop_safe_cell()
                if safe_coord is not None:
                    self.master_item_coords[item_type].append(safe_coord)
                    self.master_coords_item[safe_coord] = item_type
                else:
                    print("[Info] There's no more safe cell.")
                    break
        # Add in Agent.
        agent_coord = self.get_safe_cell()
        self.master_item_coords[Item.AGENT] = agent_coord
        self.master_coords_item[agent_coord] = Item.AGENT

    def fixed_item_input(self) -> None:
        agent_coord = (1, 1)
        wumpus_coord = (3, 1)
        coins_coord = [(2, 4), (3, 2), (5, 1)]
        portal_coord = [(1, 3), (4, 1), (4, 3)]

        self.master_item_coords[Item.AGENT] = agent_coord
        self.master_coords_item[agent_coord] = Item.AGENT
        self.master_item_coords[Item.WUMPUS] = wumpus_coord
        self.master_coords_item[wumpus_coord] = Item.WUMPUS
        self.safe_cells.remove(wumpus_coord)

        for coord in coins_coord:
            self.safe_cells.remove(coord)
            self.master_item_coords[Item.COIN].append(coord)
            self.master_coords_item[coord] = Item.COIN

        for coord in portal_coord:
            self.safe_cells.remove(coord)
            self.master_item_coords[Item.PORTAL].append(coord)
            self.master_coords_item[coord] = Item.PORTAL

    # infect surrounding cells with Stench and Confundus
    def infect_cell(self, x: int, y: int, cell_no: int, item_type: str, map: list) -> None:
        for new_x, new_y in [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]:
            # Infect cells that are not wall.
            if 0 <= new_x < MAP_X and 0 <= new_y < MAP_Y and map[new_x][new_y][1] != Map.WALL:
                map[new_x][new_y][cell_no] = item_type

    # Generate the Absolute Map based on item_coords.
    def init_abs_map(self) -> list:
        # Store 2D Array (7 x 6). Each cell is pointer to Map cell. (3 x 3)
        items = {Item.AGENT, Item.WUMPUS, Item.COIN, Item.PORTAL}
        map = [[deepcopy({1: Map.DOT, 2: Map.DOT, 3: Map.DOT, 4: Map.NO_NPC,
                          5: Map.UNVISITED, 6: Map.NO_NPC, 7: Map.DOT, 8: Map.DOT, 9: Map.DOT})
                for y in range(MAP_Y)] for x in range(MAP_X)]
        # Initalise item cells.
        for coord, item_type in self.coords_item.items():
            x, y = coord
            cell = map[x][y]
            if item_type in items:
                cell[4] = cell[6] = Map.NPC
            # Agent.
            if item_type == Item.AGENT:
                cell[1] = Map.CONFOUNDED
                cell[5] = Map.NORTH
            # Portal Item.
            elif item_type == Item.PORTAL:
                cell[5] = Map.PORTAL
                # Add Tingle indicator to affected cells.
                self.infect_cell(x, y, 3, Map.TINGLE, map)
            # Wumpus Item.
            elif item_type == Item.WUMPUS:
                cell[5] = Map.WUMPUS
                # Add stench indicator to affected cells.
                self.infect_cell(x, y, 2, Map.STENCH, map)
            elif item_type == Item.COIN:
                cell[7] = Map.GLITTER
            elif item_type == Item.WALL:
                for i in range(1, 10):
                    cell[i] = Map.WALL
        # Set to Absolute Map.
        self.abs_map = map

    def init_rel_map(self) -> list:
        # Store 2D Array (13 x 13). Each cell is pointer to Map cell. (3 x 3)
        self.rel_map = [[deepcopy({1: Map.DOT, 2: Map.DOT, 3: Map.DOT, 4: Map.NO_NPC,
                                   5: Map.UNKNOWN, 6: Map.NO_NPC, 7: Map.DOT, 8: Map.DOT, 9: Map.DOT})
                         for y in range(REL_MAP_Y)] for x in range(REL_MAP_X)]
        # Set Origin Cell.
        self.rel_map[REL_OFFSET_X][REL_OFFSET_Y][1] = Map.CONFOUNDED

    # Return the current actual cell's sensory input.
    def get_sensor_data(self, confounded=False, bump=False, scream=False) -> list[bool]:
        cell = self.abs_map[self.abs_x][self.abs_y]
        has_bump = "on" if bump else "off"
        has_confounded = "on" if confounded else "off"
        has_stench = "on" if cell[2] == Map.STENCH else "off"
        has_tingle = "on" if cell[3] == Map.TINGLE else "off"
        has_glitter = "on" if cell[7] == Map.GLITTER else "off"
        has_scream = "on" if scream else "off"
        # Print Sensory
        print("[Sensory Input] ", end="")
        print("Confounded-" if has_confounded == "on" else "C-", end="")
        print("Stench-" if has_stench == "on" else "S-", end="")
        print("Tingle-" if has_tingle == "on" else "T-", end="")
        print("Glitter-" if has_glitter == "on" else "G-", end="")
        print("Bump-" if has_bump == "on" else "B-", end="")
        print("Scream" if has_scream == "on" else "S")

        return [has_confounded, has_stench, has_tingle, has_glitter, has_bump, has_scream]

    def restart_game(self) -> None:
        # Ping Agent to Reborn.
        self.has_arrow = True
        # Transfer the original copy.
        self.item_coords = deepcopy(self.master_item_coords)
        self.coords_item = deepcopy(self.master_coords_item)
        # Initialise Coordinates.
        self.abs_orient = 0
        self.origin_coord = self.item_coords[Item.AGENT]
        self.abs_x, self.abs_y = self.item_coords[Item.AGENT]
        self.rel_x = self.rel_y = self.rel_orient = 0
        # Print out Coordinates.
        self.print_item_coordinates()
        # Generate the absolute map at the start.
        self.init_abs_map()
        # Repositon Agent through Agent.
        self.agent.reborn()
        self.agent.reposition(self.get_sensor_data(confounded=True))
        # Reset Boundary Range.
        self.rel_boundary = (5, 7)
        self.init_rel_map()

    # Start of Explore Game mode.
    def start_explore_game(self) -> None:
        # Reset everything.
        self.restart_game()
        # Available options

        # Update & Evaluate Relative Map.
        if not self.evaluate_agent(True):
            self.terminate_program()
        self.update_relative_map()
        self.render_maps()
        # Keep querying for Explore -> Move Agent until there's no more returned value for explore.
        while bool(list(self.agent.prolog.query("explore(L)", maxresult=10))):

            moves = list(self.agent.prolog.query(
                "explore(L)", maxresult=10))[0]

            moves = moves['L']
            moves = [str(m) for m in moves]
            if len(moves) == 0:
                break
            print("[Agent Explore] ", moves)

            # Virtual Movement.
            vir_arrow = self.has_arrow
            killed_wumpus = self.item_coords[Item.WUMPUS] is None
            vir_x, vir_y, vir_orient = self.abs_x, self.abs_y, self.abs_orient

            for index, move in enumerate(moves):
                if move not in Moveset.options:
                    print("[Explore] Failed - Move is not legitmate: ", move)
                    self.terminate_program()

                if move == Moveset.shoot:
                    if not vir_arrow:
                        continue
                    # Since arrow can't be stopped -> just match the same axis
                    vir_arrow = False
                    wumpus_x, wumpus_y = self.item_coords[Item.WUMPUS]
                    if (vir_orient == 0 and vir_x == wumpus_x and wumpus_y > vir_y) or \
                        (vir_orient == 90 and vir_y == wumpus_y and wumpus_x > vir_x) or \
                        (vir_orient == 180 and vir_x == wumpus_x and wumpus_y < vir_y) or \
                            (vir_orient == 270 and vir_y == wumpus_y and wumpus_x < vir_x):
                        killed_wumpus = True

                elif move == Moveset.move_forward:
                    if vir_orient == 0:
                        vir_y += 1
                    elif vir_orient == 90:
                        vir_x += 1
                    elif vir_orient == 180:
                        vir_y -= 1
                    else:
                        vir_x -= 1

                elif move == Moveset.turn_left:
                    vir_orient -= 90
                    if 0 > vir_orient:
                        vir_orient = 270

                elif move == Moveset.turn_right:
                    vir_orient += 90
                    vir_orient %= 360

                # Virtual Movements.
                try:
                    virtual_cell = self.abs_map[vir_x][vir_y]
                    if virtual_cell[5] == Map.PORTAL:
                        print("[Explore] Failed - Entered a unsafe cell (Portal).")
                        self.terminate_program()
                    elif virtual_cell[5] == Map.WUMPUS and not killed_wumpus:
                        print("[Explore] Failed - Entered a unsafe cell (Wumpus).")
                        self.terminate_program()
                    elif index != len(moves) - 1 and virtual_cell[5] == Map.WALL:
                        print(index, len(moves) - 1)
                        print("[Explore] Failed - Bumped into wall.")
                        self.terminate_program()
                    elif index == len(moves) - 1 and virtual_cell[5] == Map.VISITED:
                        # pass
                        if vir_x == self.origin_coord[0] and vir_y == self.origin_coord[1]:
                            continue
                        print("[Explore] Failed - End up in an visited cell.")
                        self.terminate_program()
                except IndexError:
                    print("[Explore] Failed - Went out of bound.")
                    self.terminate_program()

            # Actual Movement.
            for move in moves:
                self.entered_portal = False
                self.command_agent(move)
                if not self.evaluate_agent(self.entered_portal):
                    self.terminate_program()
                # Update Relative Map.
                self.update_relative_map()
                # Print Both Map.
                sleep(0.2)
                self.render_maps()

        if not(self.rel_x == 0 and self.rel_y == 0):
            print("[Explore] Failed - Agent did not return to (0, 0)")
            self.terminate_program()

        # Check relative map if there's any cell unvisited and safe and reachable.
        # Perform BFS
        queue = [(0, 0)]
        for _ in range(len(queue)):
            x, y = queue.pop(0)
            for new_x, new_y in [(x - 1, y), (x + 1, y), (x, y-1), (x, y+1)]:
                new_x, new_y = new_x + REL_OFFSET_X, new_y + REL_OFFSET_Y
                if 0 > new_x or new_x >= REL_MAP_X or 0 > new_y or new_y >= REL_MAP_Y:
                    continue
                # Either out of bound / Planted Wall.
                cell = self.rel_map[new_x][new_y]
                if cell[5] == Map.UNVISITED:
                    print("[Explore] Failed - There's unvisited but reachable cell.")
                    self.terminate_program()
                elif cell[5] == Map.WUMPUS or cell[5] == Map.PORTAL or cell[5] == Map.WALL:
                    continue
                elif cell[5] == Map.VISITED:
                    queue.append((new_x, new_y))

        print("[Explore] Passed - No more moves left.")

    # Start of Manual Game mode.
    def start_manual_game(self) -> None:
        self.restart_game()
        # Update & Evaluate Relative Map.
        if not self.evaluate_agent(True):
            self.terminate_program()
        # Print map.
        options = {"1": "shoot", "2": "moveforward", "3": "turnleft",
                   "4": "turnright", "5": "pickup", "6": "exit"}
        self.update_relative_map()
        self.render_maps()
        while True:
            print("\n+=================================================+")
            print("+ Select your action of choice.                   +")
            print("+ [1] - Shoot.                                    +")
            print("+ [2] - Move Forward.                             +")
            print("+ [3] - Turn Left.                                +")
            print("+ [4] - Turn Right.                               +")
            print("+ [5] - Pick up.                                  +")
            print("+ [6] - Exit.                                     +")
            print("+=================================================+")

            selected = input(f"[Input] Please enter your option: ")

            if selected not in options:
                print("[Error] Invalid option, please try again with (1-6).")
                continue

            if selected == "6":
                print("[Screen] Thanks for playing!")
                quit()

            self.entered_portal = False
            self.command_agent(options[selected])
            if not self.evaluate_agent(self.entered_portal):
                self.terminate_program()
            # Update Relative Map.
            self.update_relative_map()
            # Print Both Map.
            sleep(0.2)
            self.render_maps()

    def update_relative_map(self) -> None:
        # Populate Relative Map with Agent Sensors.
        for x in range(-REL_OFFSET_X, REL_OFFSET_X):
            for y in range(-REL_OFFSET_Y, REL_OFFSET_Y):
                # Current Relative Cell.
                cell = self.rel_map[x + REL_OFFSET_X][y + REL_OFFSET_Y]

                # Check if cell is a Wall -> Skip if it is.
                if self.agent.wall(x, y):
                    for i in range(1, 10):
                        cell[i] = Map.WALL
                    continue

                has_safe = self.agent.safe(x, y)
                has_wumpus = self.agent.wumpus(x, y)
                has_tingle = self.agent.tingle(x, y)
                has_stench = self.agent.stench(x, y)
                has_glitter = self.agent.glitter(x, y)
                has_visited = self.agent.visited(x, y)
                has_confundus = self.agent.confundus(x, y)
                # print(
                #   f"({x},{y})- safe: {has_safe}, has_wumpus: {has_wumpus}, visited: {has_visited}, confundus: {has_confundus}, stench:{has_stench}, glitter:{has_glitter}, tingle:{has_tingle}")
                cell[2] = Map.STENCH if has_stench else Map.DOT
                cell[3] = Map.TINGLE if has_tingle else Map.DOT
                cell[7] = Map.GLITTER if has_glitter else Map.DOT

                if self.rel_x == x and self.rel_y == y:
                    cell[4] = cell[6] = Map.NPC
                    cell[5] = Map.direction_symbol[self.rel_orient]
                elif has_wumpus and has_confundus:
                    cell[4] = cell[6] = Map.NPC
                    cell[5] = Map.UNSAFE
                elif has_wumpus:
                    cell[4] = cell[6] = Map.NPC
                    cell[5] = Map.WUMPUS
                elif has_confundus:
                    cell[4] = cell[6] = Map.NPC
                    cell[5] = Map.PORTAL
                elif has_glitter:
                    cell[4] = cell[6] = Map.NPC
                    if has_visited:
                        cell[5] = Map.VISITED
                    else:
                        cell[5] = Map.UNVISITED
                else:
                    cell[4] = cell[6] = Map.NO_NPC
                    if has_visited and has_safe:
                        cell[5] = Map.VISITED
                    elif not has_visited and has_safe:
                        cell[5] = Map.UNVISITED
                    else:
                        # Not determined yet.
                        cell[5] = Map.UNKNOWN

    def render_maps(self) -> None:
        self.render_abs_map()
        self.render_rel_map()

    def render_abs_map(self) -> None:
        print("==[Absolute Map]==")
        # Print Absolute Map.
        cell_sep = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        print("-" * 64)
        for col in reversed(range(MAP_Y)):
            for _ in range(3):
                print("| ", end="")
                for row in range(MAP_X):
                    cell = self.abs_map[row][col]
                    for cell_no in cell_sep[_]:
                        print(cell[cell_no], end=" ")
                    print(" | ", end="")
                print("")
            print("-" * 64)

    def render_rel_map(self) -> None:
        print("==[Relative Map]==")
        # Print Absolute Map.
        cell_sep = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        boundary_diff = self.rel_boundary[1] - self.rel_boundary[0] + 1
        print("-" * (9 * boundary_diff) + "-")
        for col in reversed(range(self.rel_boundary[0], self.rel_boundary[1] + 1)):
            for _ in range(3):
                print("| ", end="")
                for row in range(self.rel_boundary[0], self.rel_boundary[1] + 1):
                    cell = self.rel_map[row][col]
                    for cell_no in cell_sep[_]:
                        print(cell[cell_no], end=" ")
                    print(" | ", end="")
                print("")
            print("-" * (9 * boundary_diff) + "-")

    # Switch case, run agent movement.

    def command_agent(self, command: str) -> None:
        # 2.2.1 Driver Printout Part 2.1
        print(f"[Action] {command}")
        # Shoot
        if command == Moveset.shoot:
            self.action_shoot()
        elif command == Moveset.move_forward:
            self.action_forward()
        elif command == Moveset.turn_left:
            self.action_turn_left()
        elif command == Moveset.turn_right:
            self.action_turn_right()
        elif command == Moveset.pick_up:
            self.action_pick_up()
        else:
            print(f"[Error] Wrong Agent Command: {command}")

    # Shoot Arrow by Agent.
    def action_shoot(self) -> None:

        if not self.has_arrow:
            print("[Screen] Agent does not have any arrow left.")
            self.agent.move(Moveset.shoot, self.get_sensor_data())
            return

        killed_wumpus = False
        self.has_arrow = False
        wumpus_x, wumpus_y = self.item_coords[Item.WUMPUS]

        # Since arrow can't be stopped -> just match the same axis
        if self.abs_orient == 0 and self.abs_x == wumpus_x and wumpus_y > self.abs_y:
            killed_wumpus = True
        elif self.abs_orient == 90 and self.abs_y == wumpus_y and wumpus_x > self.abs_x:
            killed_wumpus = True
        elif self.abs_orient == 180 and self.abs_x == wumpus_x and wumpus_y < self.abs_y:
            killed_wumpus = True
        elif self.abs_orient == 270 and self.abs_y == wumpus_y and wumpus_x < self.abs_x:
            killed_wumpus = True

        if killed_wumpus is True:
            print("[Info] Wumpus has been slained -> LETS GO LAH.")
            # Remove from coords
            wumpus_coord = self.item_coords[Item.WUMPUS]
            self.item_coords[Item.WUMPUS] = None
            del self.coords_item[wumpus_coord]
            self.safe_cells.append(wumpus_coord)
            # Infect scream.
            self.abs_map[self.abs_x][self.abs_y][9] = Map.SCREAM
            self.rel_map[self.rel_x + REL_OFFSET_X][self.rel_y +
                                                    REL_OFFSET_Y][9] = Map.SCREAM
            # Update Wumpus cell.
            cell = self.abs_map[wumpus_x][wumpus_y]
            cell[5] = Map.UNVISITED
            cell[4] = cell[6] = Map.NO_NPC
            # Disinfect surrounding cell.
            self.infect_cell(wumpus_x, wumpus_y, 2, Map.DOT, self.abs_map)
            self.agent.move(Moveset.shoot, self.get_sensor_data(scream=True))
        else:
            print("[Info] Agent missed the shoot.")
            self.agent.move(Moveset.shoot, self.get_sensor_data())
        return

    def action_forward(self) -> None:
        # Check if there's a wall.
        f_abs_x, f_abs_y = self.abs_x, self.abs_y
        f_rel_x, f_rel_y = self.rel_x, self.rel_y

        if self.abs_orient == 0:
            f_abs_y, f_rel_y = f_abs_y + 1, f_rel_y + 1
        elif self.abs_orient == 90:
            f_abs_x, f_rel_x = f_abs_x + 1, f_rel_x + 1
        elif self.abs_orient == 180:
            f_abs_y, f_rel_y = f_abs_y - 1, f_rel_y - 1
        else:
            f_abs_x, f_rel_x = f_abs_x - 1, f_rel_x - 1

        # Hit a wall.
        if self.abs_map[f_abs_x][f_abs_y][1] == Map.WALL:
            print(f_abs_x, f_abs_y, self.abs_orient)
            # Induce Bump effect
            print("[Info] Bumped! There's a wall infront.")
            self.abs_map[self.abs_x][self.abs_y][8] = Map.BUMP
            self.rel_map[self.rel_x + REL_OFFSET_X][self.rel_y +
                                                    REL_OFFSET_Y][8] = Map.BUMP
            self.agent.move(Moveset.move_forward,
                            self.get_sensor_data(bump=True))
            if not self.agent.wall(f_rel_x, f_rel_y):
                wall_coord = (f_rel_x, f_rel_y)
                print("[Mapping] Failed - ", end="")
                print(f"Agent failed to map the wall at {wall_coord}.")
                self.terminate_program()
            return

        # Managed to advance forward.
        cur_cell = self.abs_map[self.abs_x][self.abs_y]
        forward_cell = self.abs_map[f_abs_x][f_abs_y]

        # Wumpus Oh no!
        if forward_cell[5] == Map.WUMPUS:
            print("[Info] Wumpus was right infront, the game is restarted.")
            self.restart_game()

        # Enters a portal.
        elif forward_cell[5] == Map.PORTAL:
            # Get a safe cell to be teleported.
            safe_coord = self.get_safe_cell()
            if safe_coord is not None:
                # Restart the Actual Map, with changes to coin, wumpus, arrow.
                original_sp = self.item_coords[Item.AGENT]
                del self.coords_item[original_sp]
                self.item_coords[Item.AGENT] = safe_coord
                self.coords_item[safe_coord] = Item.AGENT
                self.init_abs_map()
                print("[Info] Agent has been teleported.")
                # New safe location.
                self.abs_orient = 0
                self.abs_x, self.abs_y = safe_coord
                self.origin_coord = safe_coord  # For relative mapping.
                self.abs_map[self.abs_x][self.abs_y][1] = Map.CONFOUNDED
                # Reset Relative Map + Update relative position.
                self.rel_boundary = (5, 7)
                self.init_rel_map()
                self.rel_x = self.rel_y = self.rel_orient = 0
                self.agent.reposition(self.get_sensor_data(confounded=True))
                self.entered_portal = True
        else:
            print("[Info] Agent has moved forward.")
            cur_cell[5] = Map.VISITED
            # There's no NPC (include Coin) in this cell anymore.
            if cur_cell[7] != Map.GLITTER:
                cur_cell[4] = cur_cell[6] = Map.NO_NPC
            # Update forwarded cell.
            forward_cell[4] = forward_cell[6] = Map.NPC
            forward_cell[5] = Map.direction_symbol[self.abs_orient]
            # Update absolute coordinates
            self.abs_x, self.abs_y = f_abs_x, f_abs_y
            self.rel_x, self.rel_y = f_rel_x, f_rel_y
            # Expand map if neccessary
            actual_rel_x = self.rel_x + REL_OFFSET_X
            actual_rel_y = self.rel_y + REL_OFFSET_Y
            if (actual_rel_x == self.rel_boundary[0] or actual_rel_x == self.rel_boundary[1]) or \
                    (actual_rel_y == self.rel_boundary[0] or actual_rel_y == self.rel_boundary[1]):
                self.rel_boundary = (
                    self.rel_boundary[0] - 1, self.rel_boundary[1] + 1)
            # Update Prolog.
            self.agent.move(Moveset.move_forward, self.get_sensor_data())
        return

    def action_pick_up(self) -> None:
        # Remove Glitter if there is any.
        cell = self.abs_map[self.abs_x][self.abs_y]
        if cell[7] == Map.GLITTER:
            # Update Map.
            print("[Info] Agent has picked up a coin.")
            cell[7] = Map.DOT
            # Add back to safe cells.
            self.safe_cells.append((self.abs_x, self.abs_y))
            self.item_coords[Item.COIN].remove((self.abs_x, self.abs_y))
            del self.coords_item[(self.abs_x, self.abs_y)]
        else:
            print("[Info] Nothing to pick up from the ground.")
        self.agent.move(Moveset.pick_up, self.get_sensor_data())

        # Check if pickup was registered by Agent.
        if self.agent.glitter(self.rel_x, self.rel_y):
            print("[Sensory] Glitter check failed - Coin has already been picked up.")
            self.terminate_program()

    def action_turn_left(self) -> None:
        # Actual Orientation
        self.abs_orient -= 90
        if 0 > self.abs_orient:
            self.abs_orient = 270
        self.abs_map[self.abs_x][self.abs_y][5] = Map.direction_symbol[self.abs_orient]
        # Relative Orientation.
        self.rel_orient -= 90
        if 0 > self.rel_orient:
            self.rel_orient = 270
        self.agent.move(Moveset.turn_left, self.get_sensor_data())

    def action_turn_right(self) -> None:
        # Actual Orientiation.
        self.abs_orient += 90
        self.abs_orient %= 360
        self.abs_map[self.abs_x][self.abs_y][5] = Map.direction_symbol[self.abs_orient]
        # Relative Orientation.
        self.rel_orient += 90
        self.rel_orient %= 360
        self.agent.move(Moveset.turn_right, self.get_sensor_data())

    # Run Fixed Game.

    def run_auto_game(self) -> None:
        pass

    # Etc Functions
    def check_valid_coord(self, x: int, y: int) -> bool:
        if x.isnumeric() and y.isnumeric():
            if 0 <= int(x) < MAP_X and 0 <= int(y) < MAP_Y:
                return True
        return False

    def get_safe_cell(self) -> tuple:
        if len(self.safe_cells) == 0:
            print("[Info] No more safe cell in the map.")
            return None
        return random.choice(self.safe_cells)

    def pop_safe_cell(self) -> tuple:
        if len(self.safe_cells) == 0:
            print("[Info] No more safe cell in the map.")
            return None
        return self.safe_cells.pop()

    def terminate_program(self) -> None:
        print("[Driver] Terminating the programme, please fix your Agent...")
        quit()

    def evaluate_agent(self, entered_portal: bool = False) -> bool:
        # Flow / Assumption:
        # 1. Evaluate Driver's Relative against Agent's Relative.
        # 2. Compare the current relative cell only.
        # 3. (optional) Check if only step in portal.

        localisation = inference = memory = True

        # 1 Localisation: Evaluate Agent Current Position.
        d = {0: "rnorth", 90: 'reast', 180: 'rsouth', 270: "rwest"}
        if not self.agent.current(self.rel_x, self.rel_y, d[self.rel_orient]):
            localisation = False
            driver_coord = (self.rel_x, self.rel_y, d[self.rel_orient])
            a_pos = list(self.agent.prolog.query("current(X,Y,D)"))[0]
            print("[Mapping] Failed - Position mismatch ", end="")
            print(f"Driver:{driver_coord}", end=", ")
            print(f"Agent: ({a_pos['X']}, {a_pos['Y']}, {a_pos['D']})")
        elif self.agent.hasarrow() != self.has_arrow:
            localisation = False
            print("[Mapping] Failed - Arrow knowledge mismatch.")
        else:
            print("[Mapping] Passed - ", end="")
            print(f"({self.rel_x},{self.rel_y},{d[self.rel_orient]})", end="")
            print(f", Arrow: {self.has_arrow}")

        # 2. Evaluate Agent's Sensory (Entire Map)
        org_x, org_y = self.origin_coord
        rel_x_boundary = (REL_OFFSET_X - org_x, REL_OFFSET_X - org_x + MAP_X)
        rel_y_boundary = (REL_OFFSET_Y - org_y, REL_OFFSET_Y - org_y + MAP_Y)

        # 2.1 Check for Glitter
        for soln in self.agent.prolog.query("glitter(X,Y)"):
            glitter_x = soln['X'] + REL_OFFSET_X
            glitter_y = soln['Y'] + REL_OFFSET_Y
            try:
                if self.abs_map[glitter_x - rel_x_boundary[0]][glitter_y - rel_y_boundary[0]][7] != Map.GLITTER:
                    inference = False
                    print("[Inference] Glitter check failed - ", end="")
                    print("There's no glitter at ",
                          (soln['X'], soln['Y']), "yet agent think it does.")
            except IndexError:
                inference = False
                print("[Inference] Glitter check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.2 Check for Visited
        # print(list(self.agent.prolog.query("visited(X,Y)")))
        for soln in self.agent.prolog.query("visited(X,Y)"):
            visited_x = soln['X'] + REL_OFFSET_X
            visited_y = soln['Y'] + REL_OFFSET_Y
            try:
                symbol_5 = self.abs_map[visited_x - rel_x_boundary[0]]
                symbol_5 = symbol_5[visited_y - rel_y_boundary[0]][5]
                directions = {Map.NORTH, Map.SOUTH, Map.EAST, Map.WEST}
                if symbol_5 != Map.VISITED and symbol_5 not in directions:
                    inference = False
                    print("[Inference] Visited check failed - ", end="")
                    print("Agent has not visited ",
                          (soln['X'], soln['Y']), "yet it think it has.")
                    if symbol_5 == Map.WALL:
                        print("[Info]", (soln['X'], soln['Y']),
                              "contains a wall.")

            except IndexError:
                inference = False
                print("[Inference] Visited check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.3 Check for Stench
        for soln in self.agent.prolog.query("stench(X,Y)"):
            stench_x = soln['X'] + REL_OFFSET_X
            stench_y = soln['Y'] + REL_OFFSET_Y
            try:
                if self.abs_map[stench_x - rel_x_boundary[0]][stench_y - rel_y_boundary[0]][2] != Map.STENCH:
                    inference = False
                    print("[Inference] Stench check failed - ", end="")
                    print("There's no stench at ",
                          (soln['X'], soln['Y']), "yet agent think it does.")
            except IndexError:
                inference = False
                print("[Inference] Stench check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.4 Check for Tingle
        for soln in self.agent.prolog.query("tingle(X,Y)"):
            tingle_x = soln['X'] + REL_OFFSET_X
            tingle_y = soln['Y'] + REL_OFFSET_Y
            try:
                if self.abs_map[tingle_x - rel_x_boundary[0]][tingle_y - rel_y_boundary[0]][3] != Map.TINGLE:
                    inference = False
                    print("[Inference] Tingle check failed - ", end="")
                    print("There's no tingle at ",
                          (soln['X'], soln['Y']), "yet agent think it does.")
            except IndexError:
                inference = False
                print("[Inference] Tingle check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.5 Check for Safe
        for soln in self.agent.prolog.query("safe(X,Y)"):
            safe_x = soln['X'] + REL_OFFSET_X
            safe_y = soln['Y'] + REL_OFFSET_Y
            try:
                cell = self.abs_map[safe_x - rel_x_boundary[0]
                                    ][safe_y - rel_y_boundary[0]]
                if cell[5] == Map.WUMPUS or cell[5] == Map.PORTAL:
                    inference = False
                    print("[Inference] Safe check failed - ", end="")
                    print((soln['X'], soln['Y']),
                          " is not a safe coordinate, but Agent think it is.")
                    if cell[5] == Map.WUMPUS:
                        print("[Info]", (soln['X'], soln['Y']),
                              "contain Wumpus.")
                    else:
                        print("[Info]", (soln['X'], soln['Y']),
                              "contain Portal.")
            except IndexError:
                inference = False
                print("[Inference] Safe check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.6 Check for Wumpus
        for soln in self.agent.prolog.query("wumpus(X,Y)"):
            wumpus_x = soln['X'] + REL_OFFSET_X
            wumpus_y = soln['Y'] + REL_OFFSET_Y
            try:
                cell = self.abs_map[wumpus_x - rel_x_boundary[0]
                                    ][wumpus_y - rel_y_boundary[0]]
                wumpus_x = wumpus_x - rel_x_boundary[0]
                wumpus_y = wumpus_y - rel_y_boundary[0]
                # Check near by got stench
                has_stench = False
                for adj_x, adj_y in [(wumpus_x - 1, wumpus_y), (wumpus_x + 1, wumpus_y), (wumpus_x, wumpus_y - 1), (wumpus_x, wumpus_y + 1)]:
                    if 0 <= adj_x < MAP_X and 0 <= adj_y < MAP_Y:
                        if self.abs_map[adj_x][adj_y][2] == Map.STENCH:
                            has_stench = True
                            break
                if not has_stench:
                    inference = False
                    print("[Inference] Wumpus check failed - ", end="")
                    print("Agent inferred", (soln['X'], soln['Y']),
                          " has Wumpus even though there's no adjacent stench.")
            except IndexError:
                inference = False
                print("[Inference] Wumpus check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.7 Check for Portal
        for soln in self.agent.prolog.query("confundus(X,Y)"):
            portal_x = soln['X'] + REL_OFFSET_X
            portal_y = soln['Y'] + REL_OFFSET_Y
            try:
                cell = self.abs_map[portal_x - rel_x_boundary[0]
                                    ][portal_y - rel_y_boundary[0]]
                portal_x = portal_x - rel_x_boundary[0]
                portal_y = portal_y - rel_y_boundary[0]
                # Check near by got stench
                has_tingle = False
                for adj_x, adj_y in [(portal_x - 1, portal_y), (portal_x + 1, portal_y), (portal_x, portal_y - 1), (portal_x, portal_y + 1)]:
                    if 0 <= adj_x < MAP_X and 0 <= adj_y < MAP_Y:
                        if self.abs_map[adj_x][adj_y][3] == Map.TINGLE:
                            has_tingle = True
                            break
                if not has_tingle:
                    inference = False
                    print("[Inference] Confundus check failed - ", end="")
                    print("Agent inferred", (soln['X'], soln['Y']),
                          " has Portal even though there's no adjacent tingle.")

            except IndexError:
                inference = False
                print("[Inference] Confundus check failed - ", end="")
                print((soln['X'], soln['Y']), " is out of bound.")

        # 2.8 Evaluate Agent's Sensory Input for Current Cell
        cell = self.abs_map[self.abs_x][self.abs_y]
        has_safe = self.agent.safe(self.rel_x, self.rel_y)
        has_visited = self.agent.visited(self.rel_x, self.rel_y)
        has_tingle = self.agent.tingle(self.rel_x, self.rel_y)
        has_stench = self.agent.stench(self.rel_x, self.rel_y)
        has_glitter = self.agent.glitter(self.rel_x, self.rel_y)

        # [has_confounded, has_stench, has_tingle, has_glitter, has_bump, has_scream]
        if not has_visited:
            inference = False
            print("[Inference] Visited check failed - Agent is on the cell itself.")
        if not has_safe:
            inference = False
            print("[Inference] Safe check failed - Agent is on the cell itself.")
        if has_stench and cell[2] != Map.STENCH:
            inference = False
            print("[Inference] Stench check failed - Agent is on the cell itself.")
        if has_tingle and cell[3] != Map.TINGLE:
            inference = False
            print("[Inference] Tingle check failed - Agent is on the cell itself.")
        if has_glitter and cell[7] != Map.GLITTER:
            inference = False
            print("[Inference] Glitter check failed - Agent is on the cell itself.")

        if inference:
            print("[Inference] Passed")

        # 3. Enter Confudus Portal.
        if entered_portal:
            # Check if still remember arrow
            if self.agent.hasarrow() != self.has_arrow:
                memory = False
                print("[Memory Wipe] Arrow Failed.")

            for q in ["visited(X,Y)", "tingle(X,Y)", "glitter(X,Y)", "stench(X,Y)"]:
                for soln in self.agent.query(q):
                    X, Y = soln['X'], soln['Y']
                    if X != 0 or Y != 0:
                        memory = False
                        print(f"[Memory Wipe] Failed to wipe knowledge of {q}")
                        break
            for q in ["wumpus(X,Y)", "confundus(X,Y)", "safe(X,Y)"]:
                for soln in self.agent.query(q):
                    if (soln['X'], soln['Y']) not in {(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)}:
                        memory = False
                        print(f"[Memory Wipe] Failed to wipe knowledge of {q}")
                        break
            if memory:
                print("[Memory Wipe] Passed.")

        return localisation and inference and memory

    # Run Manual game
    def choose_game_mode(self) -> None:
        try:
            options = {"1", "2", "3"}
            print(GAME_MODE_NOTE)
            while True:
                # Screen.
                print("\n+=================================================+")
                print("+ Select your desired Agent movement mode.        +")
                print("+ [1] - Control your agent action manually.       +")
                print("+ [2] - Move agent through explore(L)             +")
                print("+ [3] - Exit.                                     +")
                print("+=================================================+")

                selected = input(f"[Input] Please enter your option: ")

                if selected not in options:
                    print("[Error] Invalid input, please enter (1 - 3).")
                    continue
                if selected == "1":
                    self.start_manual_game()
                elif selected == "2":
                    self.start_explore_game()
                else:
                    print("[Screen] Thanks for playing!")
                    quit()

        except KeyboardInterrupt:
            self.terminate_program()

    def print_item_coordinates(self) -> None:
        print("=" * 15)
        print("[Wumpus Map Coordinates]")
        print(f"[Agent] {self.item_coords[Item.AGENT]}")
        print(f"[Wumpus] {self.item_coords[Item.WUMPUS]}")
        print(f"[Coins] {sorted(self.item_coords[Item.COIN])}")
        print(f"[Portals] {sorted(self.item_coords[Item.PORTAL])}")
        print(f"[Walls] {sorted(self.item_coords[Item.WALL])}")
        print("=" * 15)


# Standalone testing.
if __name__ == '__main__':
    try:
        print("[Screen] Welcome to Team AlphaBlur's Wumpus World Driver...")

        file_name = None
        #file_name = "agent2.pl"

        while True:
            file_name = input("[Input] Please enter your agent file name: ")
            try:
                f = open(file_name)
                f.close()
                break
            except IOError:
                print(
                    "[Error] File doesn't exist, make sure the file is on the same directory.")
                continue
        options = {"1", "2", "3", "4"}

        while True:
            # Screen 1.
            print("\n+=================================================+")
            print("+ Select your Wumpus Map Choice.                  +")
            print("+ [1] - Manually Customised Map.                  +")
            print("+ [2] - Randomly Generated Map.                   +")
            print("+ [3] - AlphaBlur's Customised Map.               +")
            print("+ [4] - Exit.                                     +")
            print("+=================================================+")

            selected = input(f"[Input] Please enter your option: ")

            if selected not in options:
                print("[Error] Invalid input, please enter (1 - 4).")
                continue

            # Intialise Driver.
            driver = Driver(file_name)

            if selected == "1":
                driver.recv_manual_item_input()
            elif selected == "2":
                driver.generate_item_input()
            elif selected == "3":
                driver.fixed_item_input()
            else:
                raise KeyboardInterrupt()

            driver.choose_game_mode()

    except KeyboardInterrupt:
        print("[Driver] Terminating the program now...")
