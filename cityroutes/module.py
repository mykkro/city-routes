
# Insert comment here...
class Position(object):
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'Position'

    

# Insert comment here...
class Node(object):
    __slots__ = ['position']

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Node'

    

# Insert comment here...
class Edge(object):
    __slots__ = ['start', 'end']

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return 'Edge'

    


# Insert comment here...
class Road(object):
    __slots__ = ['alongEdge', 'ways', 'annotations']

    def __init__(self, alongEdge, ways, annotations):
        self.alongEdge = alongEdge
        self.ways = ways
        self.annotations = annotations

    def __repr__(self):
        return 'Road'

    


# Insert comment here...
class Way(object):
    __slots__ = ['reversed', 'segments']

    def __init__(self, reversed, segments):
        self.reversed = reversed
        self.segments = segments

    def __repr__(self):
        return 'Way'

    

# Insert comment here...
class WaySegment(object):
    __slots__ = ['length', 'annotations']

    def __init__(self, length, annotations):
        self.length = length
        self.annotations = annotations

    def __repr__(self):
        return 'WaySegment'

    


# Insert comment here...
class Lane(object):
    __slots__ = ['width', 'annotations']

    def __init__(self, width, annotations):
        self.width = width
        self.annotations = annotations

    def __repr__(self):
        return 'Lane'

    

# Insert comment here...
class BasicLane(Lane):
    __slots__ = ['width']

    def __init__(self, width):
        self.width = width

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

    def __init__(self, position, side, length):
        self.position = position
        self.side = side
        self.length = length

    def __repr__(self):
        return 'Annotation'

    

# road sign, horizontal sign on the road
class LaneAnnotation(Annotation):
    __slots__ = []

    def __init__(self):
        pass

    def __repr__(self):
        return 'LaneAnnotation'

    

# road sign, semaphore, parking
class WayAnnotation(Annotation):
    __slots__ = []

    def __init__(self):
        pass

    def __repr__(self):
        return 'WayAnnotation'

    

# Insert comment here...
class RoadAnnotation(Annotation):
    __slots__ = []

    def __init__(self):
        pass

    def __repr__(self):
        return 'RoadAnnotation'

    


# Insert comment here...
class ParkingStripParallel(WayAnnotation):
    __slots__ = ['width']

    def __init__(self, width):
        self.width = width

    def __repr__(self):
        return 'ParkingStripParallel'

    

# Insert comment here...
class ParkingStripForward(WayAnnotation):
    __slots__ = ['boxWidth', 'boxLength', 'boxAngle']

    def __init__(self, boxWidth, boxLength, boxAngle):
        self.boxWidth = boxWidth
        self.boxLength = boxLength
        self.boxAngle = boxAngle

    def __repr__(self):
        return 'ParkingStripForward'

    