from Agent import Agent
from Node import Node
from random import choice

class World:
    def __init__(self):
        self.size = (7, 6)
        self.world = []

        for _ in range(self.size[1]):
            self.world.append([Node() for _ in range(self.size[0])])
        
        self.agent = Agent(1, 1)
        self.wumpus = set([(3, 4)])
        self.coin = set([(5, 4)])
        self.portals = set([(2, 2), (4, 4)])
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

    def update_agent(self, action):
        self.agent.actions.append(action)

        # Picking up the coin from the floor
        if action == 'pickup':
            if self.agent.position in self.coin:
                self.coin.remove(self.agent.position)
                self.agent.number_of_coins += 1

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
            self.world[self.agent.position[1]][self.agent.position[0]].senses['bump'] = True
            return

        # If new position is portal, we have to teleport agent to new safe position
        # Update confounded indicator
        if (new_x, new_y) in self.portals:
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


        # If we previously bumped into a wall, and we are now moving away, we remove the bump indicator
        if 'bump' in self.world[self.agent.position[1]][self.agent.position[0]].senses:
            self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('bump', None)
        # If we previously heard a scream, we remove the scream indicator
        if 'scream' in self.world[self.agent.position[1]][self.agent.position[0]].senses:
            self.world[self.agent.position[1]][self.agent.position[0]].senses.pop('scream', None)

        self.world[self.agent.position[1]][self.agent.position[0]].occupant = None # Remove agent from previous location
        self.agent.position = (new_x, new_y) # Update location of agent
        self.agent.orientation = new_orientation # Update orientation of agent
        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent # Add agent to new location
        self.world[self.agent.position[1]][self.agent.position[0]].is_visited = True # Set new location as visited
        self.world[self.agent.position[1]][self.agent.position[0]].is_safe = True # New location is safe

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
            if neighbor_coordinates in self.portals:
                self.world[self.agent.position[1]][self.agent.position[0]].senses['tingle'] = True

    def display(self):
        for row in self.world[::-1]:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end="  ")
                print()

        print()

if __name__ == "__main__":
    w = World()
    w.display()
    while True:
        a = input()
        w.update_agent(a)
        w.display()

    