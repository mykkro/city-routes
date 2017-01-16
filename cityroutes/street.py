from roadmeshgen.Vec2d import Vec2d
from Border import Border

class RoadNode(object):
    __slots__ = ['road', 'ways']

    def __init__(self, road):
        self.road = road
        self.ways = []

    def leftBorder(self):
        # options: one or two way road
        cnt = len(self.ways)
        if cnt == 1:
            way = self.ways[0]
            if way.reversed:
                return way.rightBorder().mirror().flipped()
            else:
                return way.leftBorder()
        elif cnt == 2:
            # we expect ways[0] to be straight
            # and ways[1] to be reversed
            return self.ways[1].rightBorder().mirror().flipped()
        else:
            print "Too many ways! %d" % cnt

    def rightBorder(self):
        # options: one or two way road
        cnt = len(self.ways)
        if cnt == 1:
            way = self.ways[0]
            if way.reversed:
                return way.leftBorder().mirror().flipped()
            else:
                return way.rightBorder()
        elif cnt == 2:
            # we expect ways[0] to be straight
            # and ways[1] to be reversed
            return self.ways[0].rightBorder()
        else:
            print "Too many ways! %d" % cnt


class WayNode(object):
    __slots__ = ['way', 'segments']

    def __init__(self, way):
        self.way = way
        self.segments = []

    def widths(self):
        ww = [0] * (len(self.segments)+1)
        for i in range(0, len(self.segments)):
            ww[i] = self.segments[i].inWidth()
        ww[i+1] = self.segments[i].outWidth()
        return ww

    def length(self):
        ll = 0
        for seg in self.segments:
            ll += seg.segLength
        return ll

    def segmentAt(self, d):
        dist = 0
        for seg in self.segments:
            if (dist <= d) and (dist + seg.segLength > d):
                return (seg, d-dist)
            dist += seg.segLength
        # return last segment....
        return (self.segments[-1], self.segments[-1].segLength)

    def width(self, d):
        ss = self.segmentAt(d)
        seg = ss[0]
        off = ss[1]
        ratio = float(off)/seg.segLength
        return seg.width(ratio)

    def leftBorder(self):
        return Border.merge(map(lambda s: s.leftBorder(), self.segments))

    def rightBorder(self):
        return Border.merge(map(lambda s: s.rightBorder(), self.segments))


class SegNode(object):
    __slots__ = ['inSegment', 'outSegment', 'segLength', 'segStart', 'segment', 'lanes', 'inOffset', 'outOffset']

    def __init__(self, seg, segLength, segStart):
        self.inSegment = None
        self.outSegment = None
        self.inOffset = None
        self.outOffset = None
        self.segLength = segLength
        self.segStart = segStart
        self.segment = seg
        self.lanes = []

    def inWidth(self):
        w = 0
        for l in self.lanes:
            w += l.inWidth
        return w

    def outWidth(self):
        w = 0
        for l in self.lanes:
            w += l.outWidth
        return w

    def width(self, alpha):
        w = 0
        for l in self.lanes:
            w += l.width(alpha)
        return w

    def leftBorder(self):
        return self.lanes[0].leftBorder()

    def rightBorder(self):
        return self.lanes[-1].rightBorder()


class LaneNode(object):
    __slots__ = ['inLanes', 'inWidth', 'outLanes', 'outWidth', 'lane', 'segNode', 'inOffset', 'outOffset']

    def __init__(self, lane, segNode):
        self.inLanes = []
        self.outLanes = []
        self.inWidth = None
        self.outWidth = None
        self.inOffset = None
        self.outOffset = None
        self.lane = lane
        self.segNode = segNode

    def start(self):
        return self.segNode.segStart

    def length(self):
        return self.segNode.segLength

    def width(self, alpha):
        return alpha*self.outWidth + (1-alpha)*self.inWidth

    def leftBorder(self):
        return Border([Vec2d(0, self.inOffset), Vec2d(self.length(), self.outOffset)])

    def rightBorder(self):
        return Border([Vec2d(0, self.inOffset+self.inWidth), Vec2d(self.length(), self.outOffset+self.outWidth)])

    def body(self):
        return Border([Vec2d(0, self.inWidth), Vec2d(self.length(), self.outWidth)])
