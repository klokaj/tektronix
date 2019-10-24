class Channel:
    def __init__(self, _name):
        self.name = _name
        self.VOff = 0
        self.VPos = 0
        self.VScale = 0

    def getName(self):
        return self.name
