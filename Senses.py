class Senses:
    def __init__(self):
        self.confounded = False
        self.stench = False
        self.tingle = False
        self.glitter = False
        self.bump = False
        self.scream = False

    def reset(self):
        self.confounded = False
        self.stench = False
        self.tingle = False
        self.glitter = False
        self.bump = False
        self.scream = False

    def generate_dict(self):
        result = {}

        if self.confounded:
            result['confounded'] = True

        if self.stench:
            result['stench'] = True

        if self.tingle:
            result['tingle'] = True
        
        if self.glitter:
            result['glitter'] = True
        
        if self.bump:
            result['bump'] = True

        if self.scream:
            result['scream'] = True

        return result

    def __str__(self):
        return f"Confounded: {self.confounded}, Stench: {self.stench}, Tingle: {self.tingle}, Glitter: {self.glitter}, Bump: {self.bump}, Scream: {self.scream}"
