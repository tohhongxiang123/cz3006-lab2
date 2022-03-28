from Agent import Agent
from Node import Node


from Node import Node

class World:
    def __init__(self):
        self.size = (7, 6)
        self.world = []

        for _ in range(self.size[1]):
            self.world.append([Node() for _ in range(self.size[0])])
        
        self.agent = Agent(1, 1)
        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent

    def update_agent(self, new_x, new_y, new_orientation):
        # Update the agent's position
        self.world[self.agent.position[1]][self.agent.position[0]].occupant = None
        self.agent.position = (new_x, new_y)
        self.agent.orientation = new_orientation
        self.world[self.agent.position[1]][self.agent.position[0]].occupant = self.agent

        # Update the node's senses

    def display(self):
        for row in self.world[::-1]:
            for i in range(3):
                for node in row:
                    print(" ".join(node.get_symbols_to_print()[3*i:3*i+3]), end=" ")
                print()

        print()

if __name__ == "__main__":
    w = World()
    w.display()
    w.update_agent(3, 3, 'south')
    w.display()

    