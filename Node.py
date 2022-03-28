from Senses import Senses

class Node:
    def __init__(self):
        self.visited = False
        self.senses = {}
        self.occupant = None # One of Agent, Wumpus, Portal, Coin, Wall

    def get_symbols_to_print(self):
        symbols = ['.'] * 9

        if 'confounded' in self.senses:
            symbols[0] = '%'

        if 'stench' in self.senses:
            symbols[1] = '='

        if 'tingle' in self.senses:
            symbols[2] = 'T'

        if self.occupant is not None:
            symbols[3] = '-'
        else:
            symbols[3] = ' '

        if type(self.occupant).__name__ == "Agent":
            if self.occupant.orientation == 'north':
                symbols[4] = "^"
            elif self.occupant.orientation == 'south':
                symbols[4] = "v"
            elif self.occupant.orientation == 'east':
                symbols[4] = ">"
            else:
                symbols[4] = "<"
        else:
            symbols[4] = "?"

        if self.occupant is not None:
            symbols[5] = '-'
        else:
            symbols[5] = ' '

        if 'glitter' in self.senses:
            symbols[6] = '*'

        if 'bump' in self.senses:
            symbols[7] = 'B' # Transitory
        
        if 'scream' in self.senses:
            symbols[8] = '@' # Transitory

        return symbols
        


        