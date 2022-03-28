# W: Wall, C: Coin, A: Agent, P: Confundus portal, X: Wumpus
# 1 agent, 1 coin, 3 portals, 1 wumpus

from pyswip import Prolog
from random import randint, choice
from copy import deepcopy

from Senses import Senses

ORIENTATIONS = ['north', 'south', 'east', 'west']

class WumpusWorld:
    def __init__(self):
        self.world_size = (7, 6)

        self.agent_position = (1, 1)
        self.agent_orientation = ORIENTATIONS[0]
        self.agent_senses = Senses()
        self.agent_senses.confounded = True # Confounded in the beginning

        self.initial_agent_position = self.agent_position
        self.confundus_portal_positions = set([(3, 2), (4, 4), (1, 3)])
        self.wumpus_position = (2, 2)
        self.coin_positions = set([(4, 3)])

        self.walls = []
        self.walls += [(i, 0) for i in range(self.world_size[0])] + [(i, self.world_size[1] - 1) for i in range(self.world_size[0])]
        self.walls += [(0, i) for i in range(self.world_size[1])] + [(self.world_size[0] - 1, i) for i in range(self.world_size[1])]
        self.walls = set(self.walls)

        self.visited = {} # { (x, y): AgentSenses }
        self.db = Prolog()
        self.db.consult("db.pl")

        self.update_visited(self.agent_position[0], self.agent_position[1])

    def display(self):
        world = [[''] * self.world_size[0] for i in range(self.world_size[1])]

        for wall in self.walls:
            world[wall[1]][wall[0]] += 'X'
        
        if self.agent_orientation == 'north':
            world[self.agent_position[1]][self.agent_position[0]] += '^'
        elif self.agent_orientation == 'south':
            world[self.agent_position[1]][self.agent_position[0]] += 'v'
        elif self.agent_orientation == 'east':
            world[self.agent_position[1]][self.agent_position[0]] += '>'
        else:
            world[self.agent_position[1]][self.agent_position[0]] += '<'

        world[self.wumpus_position[1]][self.wumpus_position[0]] += 'W'

        for coin in self.coin_positions:
            world[coin[1]][coin[0]] += 'C'

        for pit in self.confundus_portal_positions:
            world[pit[1]][pit[0]] += 'O'

        for coordinate, sense in self.visited.items():
            to_display = ""
            if sense.confounded:
                to_display += "%"
            if sense.stench:
                to_display += "="
            if sense.tingle:
                to_display += "T"
            # else:
            #     to_display += "."
            if sense.glitter:
                to_display = "*"
            if sense.bump:
                to_display = "B"
            if sense.scream:
                to_display = "@"

            world[coordinate[1]][coordinate[0]] += to_display

        for row in world[::-1]:
            print(" ".join(["{:<3}".format(r) for r in row]))

    def reborn(self):
        self.agent_position = self.initial_agent_position

    def update_visited(self, x, y):
        self.visited[(x,y)] = Senses()
        self.visited[(x,y)].confounded = self.agent_senses.confounded
        self.visited[(x,y)].stench = self.agent_senses.stench
        self.visited[(x,y)].tingle = self.agent_senses.tingle
        self.visited[(x,y)].glitter = self.agent_senses.glitter
        self.visited[(x,y)].bump = self.agent_senses.bump
        self.visited[(x,y)].scream = self.agent_senses.scream

    def take_action(self, action):
        """
        Given an action, make the agent take the action
        """
        if action == 'moveforward':
            new_position = self.get_new_agent_position_after_moving_forward()
            self.update_agent_position_and_senses(new_position)
        if action == 'turn_left' or action == 'turn_right':
            self.update_agent_orientation(action)

        list(self.db.query(f"set_position(position({self.agent_position[0]},{self.agent_position[1]},{self.agent_orientation}))"))
        list(self.db.query(f"set_senses(senses({str(self.agent_senses.confounded).lower()},{str(self.agent_senses.stench).lower()},{str(self.agent_senses.tingle).lower()},{str(self.agent_senses.glitter).lower()},{str(self.agent_senses.bump).lower()},{str(self.agent_senses.scream).lower()}))"))
        

    def get_new_agent_position_after_moving_forward(self):
        """
        When the agent moves forward, return his new position
        """
        if self.agent_orientation == 'north':
            new_position = (self.agent_position[0], self.agent_position[1] + 1)
        elif self.agent_orientation == 'south':
            new_position = (self.agent_position[0], self.agent_position[1] - 1)
        elif self.agent_orientation == 'east':
            new_position = (self.agent_position[0] + 1, self.agent_position[1])
        else:
            new_position = (self.agent_position[0] - 1, self.agent_position[1])

        return new_position

    def update_agent_orientation(self, action):
        if action == 'turnleft':
            if self.agent_orientation == 'north':
                self.agent_orientation = 'west'
            elif self.agent_orientation == 'south':
                self.agent_orientation = 'east'
            elif self.agent_orientation == 'east':
                self.agent_orientation = 'north'
            else:
                self.agent_orientation = 'south'
        elif action == 'turnright':
            if self.agent_orientation == 'north':
                self.agent_orientation = 'east'
            elif self.agent_orientation == 'south':
                self.agent_orientation = 'west'
            elif self.agent_orientation == 'east':
                self.agent_orientation = 'south'
            else:
                self.agent_orientation = 'north'
        
    def update_agent_position_and_senses(self, new_position):
        """
        Given the agent's new position, update his senses, and finalise his position
        """
        self.agent_senses.reset()

        # If new position is a wall
        if new_position in self.walls: # Since position does not change when wall hits, we dont need to update senses
            self.agent_senses.bump = True
            return

        self.agent_position = new_position

        # If new position is a portal
        if new_position in self.confundus_portal_positions:
            unsafe_positions = set(list(self.confundus_portal_positions) + [self.wumpus_position] + list(self.walls))
            while True:
                new_position = (randint(1, self.world_size[0] - 1), randint(1, self.world_size[1] - 1))
                new_orientation = choice(ORIENTATIONS)
                if new_position not in unsafe_positions:
                    break

            self.agent_position = new_position
            self.agent_orientation = new_orientation
            self.agent_senses.confounded = True

        # If new position is a coin
        if new_position in self.coin_positions:
            self.agent_senses.glitter = True
            
        relative_neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for x, y in relative_neighbors:
            neighbor_x, neighbor_y = self.agent_position[0] + x, self.agent_position[1] + y
            
            # out of bounds
            if neighbor_x < 0 or neighbor_x > self.world_size[1] - 1 or neighbor_y < 0 or neighbor_y > self.world_size[0] - 1:
                continue
            
            if self.wumpus_position == (neighbor_x, neighbor_y):
                self.agent_senses.stench = True
            if (neighbor_x, neighbor_y) in self.confundus_portal_positions:
                self.agent_senses.tingle = True

        self.visited[self.agent_position] = self.agent_senses

    def get_agent_next_move(self):
        return list(self.db.query("move(A, senses)"))[0]['A']

if __name__ == "__main__":
    w = WumpusWorld()
    print(type(w))
    # w.display()

    # next_move = w.get_agent_next_move()
    # for i in range(3):
    #     w.take_action(next_move)
    #     w.display()
    #     print("")

    # w.display()