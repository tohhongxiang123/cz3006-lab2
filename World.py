from Agent import Agent
from Node import Node
from random import choice
from pyswip import Prolog
import sys

class World:
    def __init__(self):
        self.size = (7, 6)
        self.world = []

        for _ in range(self.size[1]):
            self.world.append([Node() for _ in range(self.size[0])])
        
        self.db = Prolog()
        self.db.consult('db.pl')

        self.agent_original_position = (1,1)
        self.agent = Agent(self.agent_original_position[0], self.agent_original_position[1], 'north')
        self.agent_visited_locations = set([self.agent_original_position])
        # self.wumpus = set()
        self.wumpus = set([(1, 4)])
        self.coin = set([(5, 4)])
        self.portals = set([(5,1)])
        # self.portals = set([])
        self.walls = set()

        for i in range(self.size[0]):
            self.walls.add((i,0))
            self.walls.add((i,self.size[1] - 1))
        for i in range(self.size[1]):
            self.walls.add((0, i))
            self.walls.add((self.size[0] - 1, i))

        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent
        self.world[self.agent.position[1]][self.agent.position[0]].is_visited = True
        self.world[self.agent.position[1]][self.agent.position[0]].is_safe = True
        self.world[self.agent.position[1]][self.agent.position[0]].senses['confounded'] = True
        self.db.assertz(f"visited(0,0)") # Starting agent relative position is 0,0

    def update_agent(self, action):
        if action == 'done':
            print("Complete")
            sys.exit(0)

        self.agent.actions.append(action)

        # Picking up the coin from the floor
        if action == 'pickup':
            if self.agent.position in self.coin:
                self.coin.remove(self.agent.position)
                self.agent.number_of_coins += 1
                self.db.assertz("hascoin")
                list(self.db.query("pop_path(_)"))

            if 'glitter' in self.world[self.agent.position[1]][self.agent.position[0]].senses:
                self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('glitter', None)
            
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

            coordinate_to_check = (self.agent.position[0] + to_check[0], self.agent.position[1] + to_check[1])
            while coordinate_to_check[0] >= 0 and coordinate_to_check[0] <= self.size[1] - 1 and coordinate_to_check[1] >= 0 and coordinate_to_check[1] <= self.size[0] - 1:
                if self.world[coordinate_to_check[1]][coordinate_to_check[0]].occupant == 'wumpus':
                    self.world[self.agent.position[1]][self.agent.position[0]].senses['scream'] = True
                    self.world[coordinate_to_check[1]][coordinate_to_check[0]].occupant = None
                    break

                coordinate_to_check = (coordinate_to_check[0] + to_check[0], coordinate_to_check[1] + to_check[1])
            return
            
        # actions that change the agent's position or orientation
        new_x, new_y = self.agent.position[0], self.agent.position[1]
        new_orientation = self.agent.orientation

        if action == 'moveforward':
            if self.agent.orientation == 'north':
                new_x, new_y = self.agent.position[0], self.agent.position[1] + 1
            elif self.agent.orientation == 'south':
                new_x, new_y = self.agent.position[0], self.agent.position[1] - 1
            elif self.agent.orientation == 'east':
                new_x, new_y = self.agent.position[0] + 1, self.agent.position[1]
            else:
                new_x, new_y = self.agent.position[0] - 1, self.agent.position[1]
            # list(self.db.query("move_forward"))
        elif action == 'turnleft':
            if self.agent.orientation == 'north':
                new_orientation = 'west'
            elif self.agent.orientation == 'west':
                new_orientation = 'south'
            elif self.agent.orientation == 'south':
                new_orientation = 'east'
            else:
                new_orientation = 'north'
            # list(self.db.query("turn_left"))
        elif action == 'turnright':
            if self.agent.orientation == 'north':
                new_orientation = 'east'
            elif self.agent.orientation == 'east':
                new_orientation = 'south'
            elif self.agent.orientation == 'south':
                new_orientation = 'west'
            else:
                new_orientation = 'north'
            # list(self.db.query("turn_right"))

        # If new position is a wall, do not change the agent's position
        # Update bump indicator
        if (new_x, new_y) in self.walls:
            self.world[new_y][new_x].occupant = "wall"
            self.world[self.agent.position[1]][self.agent.position[0]].senses['bump'] = True
            self.db.assertz(f"visited({new_x - self.agent_original_position[0]},{new_y - self.agent_original_position[1]})") # We bump into wall, we visited the place
            return

        # Update agent's position in db
        if action == 'moveforward':
            list(self.db.query("move_forward"))
        elif action == 'turnleft':
            list(self.db.query('turn_left'))
        elif action == 'turnright':
            list(self.db.query('turn_right'))

        # If new position is portal, we have to teleport agent to new safe position
        # Update confounded indicator
        if (new_x, new_y) in self.portals:
            self.agent_visited_locations = []
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
            list(self.db.query(f"reposition({self.world[new_y][new_x].stringify_senses()})")) # Update db

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
        self.db.assertz(f"visited({self.agent.position[0] - self.agent_original_position[0]},{self.agent.position[1] - self.agent_original_position[1]})")

        # Toh Hong Xiang wrote this. If this person isn't Toh Hong Xiang, he/she took my code without even checking
        current_position = self.agent.position
        # If agent standing on a coin, glitter
        if current_position in self.coin:
            self.world[self.agent.position[1]][self.agent.position[0]].senses['glitter'] = True
        
        # If agent stands on wumpus, game ends
        if current_position in self.wumpus:
            raise Exception("Game ended, you died to wumpus")

        # Update senses based on neighbors
        relative_neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x, y in relative_neighbors:
            neighbor_x, neighbor_y = self.agent.position[0] + x, self.agent.position[1] + y

            # Ignore out of bounds
            if neighbor_x < 0 or neighbor_x > self.size[1] - 1 or neighbor_y < 0 or neighbor_y > self.size[0] - 1:
                continue

            neighbor_coordinates = (neighbor_x, neighbor_y)

            if neighbor_coordinates in self.wumpus:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['stench'] = True
                self.db.assertz(f"stench({self.agent.position[0]},{self.agent.position[1]})")
            if neighbor_coordinates in self.portals:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['tingle'] = True
                self.db.assertz(f"tingle({self.agent.position[0]},{self.agent.position[1]})")

        

    def get_next_move(self):
        current_senses = self.world[self.agent.position[1]][self.agent.position[0]].stringify_senses()
        move = list(self.db.query(f"move(A, {current_senses})"))[0]['A']
        return move

    def display_initial_world(self):
        world = []
        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                n = Node()
                if (x, y) == self.agent_original_position:
                    print(self.agent)
                    n.occupant = self.agent
                elif (x, y) in self.wumpus:
                    n.occupant = "wumpus"
                elif (x, y) in self.coin:
                    n.occupant = "coin"
                elif (x, y) in self.portals:
                    n.occupant = "portal"

                row.append(n)
            world.append(row)

        for row in world[::-1]:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end="  ")
                print()
        print()

    def display_relative_world(self):
        world = []
        relative_travelled_coordinates = set([(x - self.agent_original_position[0], y - self.agent_original_position[1]) for x, y in self.agent_visited_locations])
        max_x = max([abs(c[0]) for c in relative_travelled_coordinates]) + 1
        max_y = max([abs(c[1]) for c in relative_travelled_coordinates]) + 1
        max_coord = max(max_x, max_y)

        for y in range(-max_coord + 1, max_coord):
            row = []
            for x in range(-max_coord + 1, max_coord):
                absolute_x = x + self.agent_original_position[0]
                absolute_y = y + self.agent_original_position[1]

                if absolute_x < 0 or absolute_x > self.size[0] - 1 or absolute_y < 0 or absolute_y > self.size[1] - 1:
                    row.append(Node())
                else:
                    row.append(self.world[absolute_y][absolute_x])

            world.append(row)

        for row in world[::-1]:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end="  ")
                print()
        print()



if __name__ == "__main__":
    w = World()
    w.display_initial_world()
    while True:
        next_move = w.get_next_move()
        w.update_agent(next_move)

        print(next_move)
        w.display_relative_world()
        print(w.world[w.agent.position[1]][w.agent.position[0]].print_out_senses())

        input()

    