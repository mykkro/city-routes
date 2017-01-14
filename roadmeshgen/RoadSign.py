class RoadSign(object):
    __slots__ = ["shape", "position", "type", "name", "rotation"]

    def __init__(self, shape, type, position, rotation, name):
        self.shape = shape # which shape?
        self.position = position
        self.rotation = rotation
        self.name = name
        self.type = type
