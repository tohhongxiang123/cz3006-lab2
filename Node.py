from Senses import Senses

class Node:
    def __init__(self):
        self.visited = False
        self.senses = {}
        self.occupant = None # One of Agent, Wumpus, Portal, Coin, Wall
        self.is_safe = False

    def stringify_senses(self):
        senses = []
        #confounded, stench, tingle, glitter, bump, scream

        senses.append('true' if 'confounded' in self.senses else 'false')
        senses.append('true' if 'stench' in self.senses else 'false')
        senses.append('true' if 'tingle' in self.senses else 'false')
        senses.append('true' if 'glitter' in self.senses else 'false')
        senses.append('true' if 'bump' in self.senses else 'false')
        senses.append('true' if 'scream' in self.senses else 'false')

        return "[" + ",".join(senses) + "]"

    def print_out_senses(self):
        senses = []
        #confounded, stench, tingle, glitter, bump, scream

        senses.append('confounded' if 'confounded' in self.senses else 'c')
        senses.append('stench' if 'stench' in self.senses else 's')
        senses.append('tingle' if 'tingle' in self.senses else 't')
        senses.append('glitter' if 'glitter' in self.senses else 'g')
        senses.append('bump' if 'bump' in self.senses else 'b')
        senses.append('scream' if 'scream' in self.senses else 's')

        return "[" + "-".join(senses) + "]"

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
        elif self.occupant == "wumpus":
            symbols[4] = "W"
        elif self.occupant == "portal":
            symbols[4] = "O"
        elif self.occupant == "coin":
            symbols[4] = "C"
        elif self.occupant == "wall":
            symbols[4] = "X"
        elif self.is_safe:
            if self.is_visited:
                symbols[4] = 'S'
            else:
                symbols[4] = 's'
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
        


        