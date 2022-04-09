from math import floor
from Agent import Agent
from Node import Node
from random import choice
from pyswip import Prolog
import sys

def rotate(arr, number_of_90_degree_clockwise_rotations):
    """
    Given a 2d array, rotate it
    """
    result = arr
    
    for i in range(number_of_90_degree_clockwise_rotations):
        list_of_tuples = zip(*result[::-1])
        result = [list(elem) for elem in list_of_tuples]
    return result

def rotate_orientation(orientation, number_of_90_degree_clockwise_rotations):
    orientations = ['north', 'east', 'south', 'west']
    current_index = orientations.index(orientation)
    new_index = (current_index + number_of_90_degree_clockwise_rotations) % len(orientations)
    return orientations[new_index]

class World:
    def __init__(self, agent_original_position = (1, 1), agent_original_orientation = 'north', wumpus_positions = [], coin_positions = [], portal_positions = [], wall_positions = [], world_size = (7, 6)):
        self.size = world_size
        self.world = []
        
        self.db = Prolog()
        self.db.consult('db.pl')
        # self.db.consult('U2022912F_Agent.pl')

        self.starting_arguments = locals()
        self.starting_arguments.pop("self", None) # Remove unrequired arguments
        self.starting_arguments.pop("world_size", None)
        self.starting_arguments.pop("_", None)
        
        self.initialise_world(**self.starting_arguments)
        self.world_size = world_size

    def initialise_world(self, agent_original_position, agent_original_orientation, wumpus_positions, coin_positions, portal_positions, wall_positions):
        self.agent_original_position = agent_original_position
        self.agent_original_orientation = agent_original_orientation
        self.agent = Agent(self.agent_original_position[0], self.agent_original_position[1], self.agent_original_orientation)
        self.agent_visited_locations = set([self.agent_original_position])
        
        self.wumpus = set(wumpus_positions)
        self.coin = set(coin_positions)
        self.portals = set(portal_positions)
        self.walls = set()
        
        self.world = []
        for _ in range(self.size[1]):
            self.world.append([Node() for _ in range(self.size[0])])

        for i in range(self.size[0]):
            self.walls.add((i,0))
            self.walls.add((i,self.size[1] - 1))
        for i in range(self.size[1]):
            self.walls.add((0, i))
            self.walls.add((self.size[0] - 1, i))

        for wall in wall_positions:
            self.walls.add(wall)

        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent
        self.world[self.agent.position[1]][self.agent.position[0]].is_visited = True
        self.world[self.agent.position[1]][self.agent.position[0]].is_safe = True
        self.world[self.agent.position[1]][self.agent.position[0]].senses['confounded'] = True
        current_position = self.agent.position

        if current_position in self.coin:
            self.world[self.agent.position[1]][self.agent.position[0]].senses['glitter'] = True
        # If agent stands on wumpus, game ends
        if current_position in self.wumpus:
            print("Died to wumpus, reset game")
            list(self.db.query("reborn"))
            self.initialise_world(**self.starting_arguments)
        
        relative_neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x, y in relative_neighbors:
            neighbor_x, neighbor_y = self.agent.position[0] + x, self.agent.position[1] + y

            # Ignore out of bounds
            if neighbor_x < 0 or neighbor_x > self.size[1] - 1 or neighbor_y < 0 or neighbor_y > self.size[0] - 1:
                continue

            neighbor_coordinates = (neighbor_x, neighbor_y)

            if neighbor_coordinates in self.wumpus:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['stench'] = True
            if neighbor_coordinates in self.portals:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['tingle'] = True
        agent_relative_position = list(self.db.query("current(X, Y, Z)"))[0]
        current_node = self.world[self.agent.position[1]][self.agent.position[0]]

        if 'stench' in current_node.senses:
            self.db.assertz(f'stench({agent_relative_position["X"]},{agent_relative_position["Y"]})')
        
        if 'tingle' in current_node.senses:
            self.db.assertz(f'tingle({agent_relative_position["X"]},{agent_relative_position["Y"]})')
        
        if 'glitter' in current_node.senses:
            self.db.assertz(f'glitter({agent_relative_position["X"]},{agent_relative_position["Y"]})')
        
        if 'bump' in current_node.senses:
            self.db.assertz(f'bump({agent_relative_position["X"]},{agent_relative_position["Y"]})')
        
        if 'scream' in current_node.senses:
            self.db.assertz(f'scream({agent_relative_position["X"]},{agent_relative_position["Y"]})')
        
    def update_agent(self, action):
        """
        Given an action, update the agent
        Actions are one of: shoot, moveforward, turnleft, turnright, pickup
        """
        self.agent.actions.append(action)

        # Picking up the coin from the floor
        if action == 'pickup':
            if self.agent.position in self.coin:
                self.coin.remove(self.agent.position)
                self.agent.number_of_coins += 1

            self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('glitter', None)
            updated_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
            list(self.db.query(f"move({action}, {updated_senses})"))
            return

        # Shooting the wumpus
        if action == 'shoot':
            if not self.agent.has_arrow:
                print("No arrow")
                return

            self.agent.has_arrow = False

            to_check = (0,0)
            if self.agent.orientation == 'north':
                to_check = (0, 1)
            elif self.agent.orientation == 'south':
                to_check = (0, -1)
            elif self.agent.orientation == 'east':
                to_check = (1, 0)
            else:
                to_check = (-1, 0)

            # Check all nodes in front of the agent
            coordinate_to_check = (self.agent.position[0] + to_check[0], self.agent.position[1] + to_check[1])
            while coordinate_to_check[0] >= 0 and coordinate_to_check[0] <= self.size[1] - 1 and coordinate_to_check[1] >= 0 and coordinate_to_check[1] <= self.size[0] - 1:
                if coordinate_to_check in self.wumpus: # If coordinate is a wumpus
                    self.world[self.agent.position[1]][self.agent.position[0]].senses['scream'] = True # Scream
                    self.world[coordinate_to_check[1]][coordinate_to_check[0]].occupant = None # Remove wumpus from node
                    self.wumpus.remove(coordinate_to_check) # Remove wumpus from node

                    to_remove_stench = [(coordinate_to_check[0] - 1, coordinate_to_check[1]), (coordinate_to_check[0] + 1, coordinate_to_check[1]), (coordinate_to_check[0], coordinate_to_check[1] - 1), (coordinate_to_check[0], coordinate_to_check[1]+ 1)]
                    for x, y in to_remove_stench:
                        self.world[y][x].senses.pop('stench', None)
                    break

                coordinate_to_check = (coordinate_to_check[0] + to_check[0], coordinate_to_check[1] + to_check[1])
            
            updated_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
            list(self.db.query(f"move({action}, {updated_senses})"))
            return
            
        # actions that change the agent's position or orientation
        new_x, new_y = self.agent.position[0], self.agent.position[1]
        new_orientation = self.agent.orientation

        # Update the position of the agent on the driver
        if action == 'moveforward':
            if self.agent.orientation == 'north':
                new_x, new_y = self.agent.position[0], self.agent.position[1] + 1
            elif self.agent.orientation == 'south':
                new_x, new_y = self.agent.position[0], self.agent.position[1] - 1
            elif self.agent.orientation == 'east':
                new_x, new_y = self.agent.position[0] + 1, self.agent.position[1]
            else:
                new_x, new_y = self.agent.position[0] - 1, self.agent.position[1]
        elif action == 'turnleft':
            if self.agent.orientation == 'north':
                new_orientation = 'west'
            elif self.agent.orientation == 'west':
                new_orientation = 'south'
            elif self.agent.orientation == 'south':
                new_orientation = 'east'
            else:
                new_orientation = 'north'
        elif action == 'turnright':
            if self.agent.orientation == 'north':
                new_orientation = 'east'
            elif self.agent.orientation == 'east':
                new_orientation = 'south'
            elif self.agent.orientation == 'south':
                new_orientation = 'west'
            else:
                new_orientation = 'north'

        # If new position is a wall, do not change the agent's position
        # Update bump indicator
        if (new_x, new_y) in self.walls:
            self.world[new_y][new_x].occupant = "wall"
            # TODO include assertz(wall(X, Y))

            self.world[self.agent.position[1]][self.agent.position[0]].senses['bump'] = True
            updated_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
            list(self.db.query(f"move({action}, {updated_senses})"))
            return

        # If new position is portal, we have to teleport agent to new safe position
        # Update confounded indicator
        if (new_x, new_y) in self.portals:
            self.agent_visited_locations = set()
            safe_positions = []
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if self.world[j][i].is_safe:
                        safe_positions.append((i, j))

                    # Reset the node since we lose all sensory readings
                    self.world[j][i].senses = {}
                    self.world[j][i].is_safe = False
                    self.world[j][i].visited = False
                    self.world[j][i].occupant = None
                    self.agent.actions = []

            # Choose new random position and orientation
            new_x, new_y = choice(safe_positions)
            new_orientation = choice(['north', 'south', 'east', 'west'])

            self.world[new_y][new_x].senses['confounded'] = True
            self.agent_original_position = (new_x, new_y) # Reset the original position
            self.agent_original_orientation = new_orientation
            self.agent_visited_locations.add((new_x, new_y))
            self.agent.position = (new_x, new_y)
            self.agent.orientation = new_orientation
            list(self.db.query(f"reposition({self.world[new_y][new_x].stringify_senses()})")) # Update agent
            return

        # If we previously bumped into a wall, and we are now moving away, we remove the bump indicator
        if 'bump' in self.world[self.agent.position[1]][self.agent.position[0]].senses:
            self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('bump', None)
        # If we previously heard a scream, we remove the scream indicator
        if 'scream' in self.world[self.agent.position[1]][self.agent.position[0]].senses:
            self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('scream', None)

        self.world[self.agent.position[1]][self.agent.position[0]].occupant = None # Remove agent from previous location
        self.agent.position = (new_x, new_y) # Update location of agent
        self.agent.orientation = new_orientation # Update orientation of agent
        self.agent_visited_locations.add((new_x, new_y)) # Add this location to visited
        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent # Add agent to new location
        self.world[self.agent.position[1]][self.agent.position[0]].is_visited = True # Set new location as visited
        self.world[self.agent.position[1]][self.agent.position[0]].is_safe = True # New location is safe

        current_position = self.agent.position

        if current_position in self.coin:
            self.world[self.agent.position[1]][self.agent.position[0]].senses['glitter'] = True
        # If agent stands on wumpus, game ends
        if current_position in self.wumpus:
            print("Died to wumpus, reset game")
            list(self.db.query("reborn"))
            self.initialise_world(**self.starting_arguments)
            return
        
        relative_neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x, y in relative_neighbors:
            neighbor_x, neighbor_y = self.agent.position[0] + x, self.agent.position[1] + y

            # Ignore out of bounds
            if neighbor_x < 0 or neighbor_x > self.size[1] - 1 or neighbor_y < 0 or neighbor_y > self.size[0] - 1:
                continue

            neighbor_coordinates = (neighbor_x, neighbor_y)

            if neighbor_coordinates in self.wumpus:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['stench'] = True
            if neighbor_coordinates in self.portals:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['tingle'] = True

        # Update senses based on neighbors
        updated_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
        list(self.db.query(f"move({action}, {updated_senses})"))

    def get_next_move(self):
        """
        Gets the next move from the agent. If there are no moves remaining, the game is ended
        """
        moves = list(self.db.query(f"explore(L)"))[0]['L']

        if len(moves) == 0:
            self.close_game()

        return [str(x) for x in moves]

    def perform_agent_action(self, action):
        """
        Executes `action` and passes in the agent's current senses as well
        """
        current_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
        return list(self.db.query(f"move({action}, {current_senses})"))

    def display_initial_world(self):
        world = []

        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                n = Node()
                if (x, y) == self.agent_original_position:
                    n.occupant = Agent(*self.agent_original_position, self.agent_original_orientation)
                elif (x, y) in self.wumpus:
                    n.occupant = "wumpus"
                elif (x, y) in self.coin:
                    n.occupant = "coin"
                elif (x, y) in self.portals:
                    n.occupant = "portal"
                elif (x, y) in self.walls:
                    n.occupant = "wall"

                row.append(n)
            world.append(row)

        world = world[::-1]

        for row in world:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end="  ")
                print()
        print()

    def display_relative_world(self):
        rotations_required = 0
        if self.agent_original_orientation == "east":
            rotations_required = 3
        elif self.agent_original_orientation == "south":
            rotations_required = 2
        elif self.agent_original_orientation == "west":
            rotations_required = 1

        world = []
        relative_safe_locations = list(self.db.query("safe(X,Y)"))
        relative_safe_locations = set([(location['X'], location['Y']) for location in relative_safe_locations])
        
        relative_visited_locations = list(self.db.query("visited(X, Y)"))
        relative_visited_locations = set([(location['X'], location['Y']) for location in relative_visited_locations])
        
        relative_glitter_locations = list(self.db.query("glitter(X, Y)"))
        relative_glitter_locations = set([(location['X'], location['Y']) for location in relative_glitter_locations])

        relative_wumpus_locations = list(self.db.query("wumpus(X, Y)"))
        relative_wumpus_locations = set([(location['X'], location['Y']) for location in relative_wumpus_locations])
        
        relative_portal_locations = list(self.db.query("confundus(X, Y)"))
        relative_portal_locations = set([(location['X'], location['Y']) for location in relative_portal_locations])

        relative_wall_locations = list(self.db.query("wall(X,Y)"))
        relative_wall_locations = set([(location['X'], location['Y']) for location in relative_wall_locations])

        relative_travelled_coordinates = set([(x - self.agent_original_position[0], y - self.agent_original_position[1]) for x, y in self.agent_visited_locations])
        max_x = max([abs(c[0]) for c in relative_travelled_coordinates]) + 2
        max_y = max([abs(c[1]) for c in relative_travelled_coordinates]) + 2
        max_coord = max(max_x, max_y)

        for y in range(-max_coord + 1, max_coord):
            row = []
            for x in range(-max_coord + 1, max_coord):
                absolute_x = x + self.agent_original_position[0]
                absolute_y = y + self.agent_original_position[1]
                if absolute_x < 0 or absolute_x > self.size[0] - 1 or absolute_y < 0 or absolute_y > self.size[1] - 1:
                    row.append(Node())
                elif self.agent.position == (absolute_x, absolute_y):
                    new_agent_orientation = rotate_orientation(self.agent.orientation, rotations_required)
                    a = Agent(self.agent.position[0], self.agent.position[1], new_agent_orientation)
                    n = Node()
                    n.senses = self.world[absolute_y][absolute_x].senses
                    n.is_safe = self.world[absolute_y][absolute_x].is_safe
                    n.occupant = a
                    n.is_visited = self.world[absolute_y][absolute_x].is_visited
                    row.append(n)
                else:
                    n = Node()
                    n.senses = self.world[absolute_y][absolute_x].senses
                    n.is_safe = self.world[absolute_y][absolute_x].is_safe
                    n.occupant = self.world[absolute_y][absolute_x].occupant
                    n.is_visited = self.world[absolute_y][absolute_x].is_visited
                    row.append(n)

            world.append(row)

        world = world[::-1]
        world = rotate(world, rotations_required)

        for absolute_y in range(len(world)):
            for absolute_x in range(len(world[absolute_y])):
                relative_coordinates = (absolute_x - floor(len(world[absolute_y]) / 2), floor(len(world) / 2) - absolute_y)
                world[absolute_y][absolute_x].is_visited = relative_coordinates in relative_visited_locations
                world[absolute_y][absolute_x].is_safe = relative_coordinates in relative_safe_locations

                if relative_coordinates in relative_wumpus_locations and relative_coordinates in relative_portal_locations:
                    world[absolute_y][absolute_x].occupant = "unknown"
                elif relative_coordinates in relative_wumpus_locations:
                    world[absolute_y][absolute_x].occupant = "wumpus"
                elif relative_coordinates in relative_portal_locations:
                    world[absolute_y][absolute_x].occupant = "portal"
                elif relative_coordinates in relative_wall_locations:
                    world[absolute_y][absolute_x].occupant = "wall"

        print(self.world[self.agent.position[1]][self.agent.position[0]].format_senses_to_print())
        for row in world:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end="  ")
                print()
        print()

    def close_game(self):
        print("Complete")
        print("Number of coins:", self.agent.number_of_coins)
        print("Actions:", self.agent.actions)
        sys.exit(0)

if __name__ == "__main__":
    # w = World(agent_original_position=(1, 1), agent_original_orientation='east', wumpus_positions=[(1, 4)], coin_positions=[(2, 2)], portal_positions=[(5,1)])
    # w = World(agent_original_position=(1, 1), agent_original_orientation='north', wumpus_positions=[(1, 4)], coin_positions=[], portal_positions=[(5,1)])
    # w = World(agent_original_position=(1, 1), agent_original_orientation='east', wumpus_positions=[(2,1)], coin_positions=[], portal_positions=[(5,1)])
    # w = World(agent_original_position=(1, 2), agent_original_orientation='east', wumpus_positions=[(2,1)], coin_positions=[(3, 1)], portal_positions=[(5,1)])
    # w = World(agent_original_position=(1, 1), agent_original_orientation='south', wumpus_positions=[(2, 2)], coin_positions=[(3, 1), (3, 3)], portal_positions=[(5,1)])
    w = World(agent_original_position=(1, 1), agent_original_orientation='south', wumpus_positions=[(2, 2)], coin_positions=[(4, 2)], portal_positions=[(5,1)])
    # w = World(agent_original_position=(1, 1), agent_original_orientation='south', wumpus_positions=[], coin_positions=[(5, 2)], portal_positions=[(3,1), (3, 3), (3, 5)])
    # w = World(agent_original_position=(1, 1), agent_original_orientation='south', wumpus_positions=[(6,6)], coin_positions=[(6, 5)], portal_positions=[(3,1), (3, 3), (3, 5)], world_size=(10,10))
    # w = World(agent_original_position=(3, 4), agent_original_orientation='south', wumpus_positions=[(2, 5)], coin_positions=[(8,8), (3, 3)], portal_positions=[(5, 3), (1, 7), (6, 8)], world_size=(10,10))
    # w = World(agent_original_position=(3, 2), agent_original_orientation='west', wumpus_positions=[(1, 3)], coin_positions=[(1, 2)], portal_positions=[(1, 1)], world_size=(5,5))
    # w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8)], portal_positions=[(5, 3), (1, 7), (6, 8)], world_size=(10,10))
    # w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8)], portal_positions=[(5, 3), (1, 7)], wall_positions=[(7,7), (8,7), (4, 4)], world_size=(10,10))
    # w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8), (3,2)], portal_positions=[(5, 3), (1, 7)], wall_positions=[(7,7), (8,7), (4, 4), (2, 2), (2, 3), (3, 3), (4, 3), (4, 2), (7, 4)], world_size=(10,10))
    
    print("=== INITIAL WORLD ===")
    w.display_initial_world()

    print("=== RELATIVE WORLD ===")
    w.display_relative_world()

    while True:
        next_move = w.get_next_move()[0]
        w.update_agent(next_move)
        print(next_move)
        w.display_relative_world()
        # print("Safes", list(w.db.query("safe(X, Y)")))
        # print("Wals", list(w.db.query("wall(X,Y)")))
        input()

        # next_moves = w.get_next_move()
        # for next_move in next_moves:
        #     w.update_agent(next_move)
        #     print(next_move)
        #     w.display_relative_world()
        #     input()