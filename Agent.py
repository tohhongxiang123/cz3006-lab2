from Senses import Senses

class Agent:
    def __init__(self, x = 0, y = 0, orientation = 'north'):
        self.position = (x, y)
        self.has_arrow = True
        self.number_of_coins = 0
        self.orientation = 'north'
        self.actions = []
        self.visited = []

    