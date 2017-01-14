from roadmeshgen.Vec2d import Vec2d


# Insert comment here...
class Position(object):
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def vec2d(self):
        return Vec2d(self.x, self.y)

    def __repr__(self):
        return 'Position(%.1f,%.1f)' % (self.x, self.y)


# Insert comment here...
class Node(object):
    __slots__ = ['position']

    def __init__(self, position=Position(0,0)):
        self.position = position

    def __repr__(self):
        return 'Node(position=%s)' % str(self.position)


# Insert comment here...
class Edge(object):
    __slots__ = ['start', 'end']

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def __repr__(self):
        return 'Edge(start=%s,end=%s)' % (str(self.start), str(self.end))

    def length(self):
        return self.start.position.vec2d().get_distance(self.end.position.vec2d())


# Insert comment here...
class Road(object):
    __slots__ = ['alongEdge', 'ways', 'annotations']

    def __init__(self, alongEdge=None, ways=[], annotations=[]):
        self.alongEdge = alongEdge
        self.ways = ways
        self.annotations = annotations

    def __repr__(self):
        return 'Road'

    def length(self):
        return self.alongEdge.length()

    def explain(self):
        return """
Road
    from (%.1f,%.1f) to (%.1f,%.1f)
    length: %s
""" % (
            self.alongEdge.start.position.x, self.alongEdge.start.position.y, self.alongEdge.end.position.x, self.alongEdge.end.position.y,
            self.length()
        )


# Insert comment here...
class Way(object):
    __slots__ = ['reversed', 'segments']

    def __init__(self, reversed=False, segments=[]):
        self.reversed = reversed
        self.segments = segments

    def __repr__(self):
        return 'Way'


# Insert comment here...
class WaySegment(object):
    __slots__ = ['length', 'annotations', 'lanes']

    def __init__(self, length=None, annotations=[], lanes=[]):
        self.length = length
        self.annotations = annotations
        self.lanes = lanes

    def __repr__(self):
        return 'WaySegment'


# Insert comment here...
class Lane(object):
    def __repr__(self):
        return 'Lane'


# Insert comment here...
class BasicLane(Lane):
    __slots__ = ['width', 'annotations']

    def __init__(self, width, annotations):
        self.width = width
        self.annotations = annotations

    def __repr__(self):
        return 'BasicLane'


# lane will split into multiple lanes
class SplitLane(Lane):
    __slots__ = ['number']

    def __init__(self, number=2):
        self.number = number

    def __repr__(self):
        return 'SplitLane'


# several neighboring lanes will merge into one
class JoinLane(Lane):
    __slots__ = ['number']

    def __init__(self, number=2):
        self.number = number

    def __repr__(self):
        return 'JoinLane'


# Insert comment here...
class AnnotationSide:
    Center, Left, Right = range(3)


# Insert comment here...
class Annotation(object):
    __slots__ = ['position', 'side', 'length']

    def __init__(self, position=None, side=AnnotationSide.Right, length=None):
        self.position = position
        self.side = side
        self.length = length

    def __repr__(self):
        return 'Annotation'


# road sign, horizontal sign on the road
class LaneAnnotation(Annotation):
    __slots__ = []

    def __repr__(self):
        return 'LaneAnnotation'


# road sign, semaphore, parking
class WayAnnotation(Annotation):
    __slots__ = []

    def __repr__(self):
        return 'WayAnnotation'


# Insert comment here...
class RoadAnnotation(Annotation):
    __slots__ = []

    def __repr__(self):
        return 'RoadAnnotation'


# Insert comment here...
class ParkingStripParallel(WayAnnotation):
    __slots__ = ['width']

    def __init__(self, position=None, side=AnnotationSide.Right, length=None, width=3.0):
        super(ParkingStripParallel, self).__init__(position=position, side=side, length=length)
        self.width = width

    def __repr__(self):
        return 'ParkingStripParallel'


# Insert comment here...
class ParkingStripForward(WayAnnotation):
    __slots__ = ['boxWidth', 'boxLength', 'boxAngle']

    def __init__(self, position=None, side=AnnotationSide.Right, length=None, boxWidth=3.0, boxLength=4.5, boxAngle=90.0):
        super(ParkingStripForward, self).__init__(position=position, side=side, length=length)
        self.boxWidth = boxWidth
        self.boxLength = boxLength
        self.boxAngle = boxAngle

    def __repr__(self):
        return 'ParkingStripForward'
