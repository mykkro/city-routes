from OPoint2d import OPoint2d

class RoadMarker(object):
    __slots__ = ['pt', 'width', 'offset']

    def __init__(self, pt, width=50, offset=0):
        self.pt = pt
        self.width = width
        self.offset = offset

    def __repr__(self):
        return 'RoadMarker(point=%s, width=%s, offset=%s)' % (self.pt, self.width, self.offset)

    def leftOffset(self):
        return -self.width/2 + self.offset

    def rightOffset(self):
        return self.width/2 + self.offset

    def reversed(self):
        return RoadMarker(OPoint2d(self.pt.p, -self.pt.v), self.width, self.offset)
