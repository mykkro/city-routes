from roadmeshgen.Vec2d import Vec2d



def readAnnotation(data):
    print "Reading annotation:", data
    type = data["$type"]
    position = data.get("position", 0.0)
    length = data.get("length", 0.0)
    sideMap = {
        "center": AnnotationSide.Center,
        "left": AnnotationSide.Left,
        "right": AnnotationSide.Right
    }
    if type == "ParkingStripForward":
        side = sideMap[data.get("side", "right")]
        boxLength = data["boxLength"]
        boxWidth = data["boxWidth"]
        boxAngle = data["boxAngle"]
        return ParkingStripForward(position, side, length, boxWidth, boxLength, boxAngle)
    elif type == "Sign":
        side = sideMap[data.get("side", "right")]
        name = data["name"]
        return Sign(name, position, side)
    elif type == "TrafficLight":
        side = sideMap[data.get("side", "right")]
        return TrafficLight(position, side, TrafficLightType.Normal, orientation=0.0)
    elif type =="ParkingStripParallel":
        side = sideMap[data.get("side", "right")]
        width = data["width"]
        return ParkingStripParallel(position, side, length, width)
    elif type =="Crossing":
        width = data["width"]
        return Crossing(position, width)
    else:
        print "Unsupported annotation: %s" % type

    return None

def readWay(data):
    segments = map(lambda w: readSegment(w), data["segments"])
    annotations = map(lambda w: readAnnotation(w), data["annotations"])
    reversed = data["reversed"] if "reversed" in data else False
    name = data.get("name")
    return Way(segments=segments, annotations=annotations, reversed=reversed, name=name)


def readSegment(data):
    lanes = map(lambda w: readLane(w), data["lanes"])
    annotations = map(lambda w: readAnnotation(w), data["annotations"])
    length = data["length"] if "length" in data else None
    name = data.get("name")
    return WaySegment(lanes=lanes, annotations=annotations, length=length, name=name)

def readLane(data):
    name = data.get("name")
    annotations = map(lambda w: readAnnotation(w), data["annotations"] if "annotations" in data else [])
    type = data["$type"]
    sideMap = {
        "center": AnnotationSide.Center,
        "left": AnnotationSide.Left,
        "right": AnnotationSide.Right
    }
    if type == "BasicLane":
        width = data["width"] if "width" in data else 3.0
        return BasicLane(width, annotations, name)
    elif type == "SplitLane":
        number = data["number"] if "number" in data else 2
        side = data["side"] if "side" in data else "right"
        return SplitLane(number, annotations, side=sideMap[side], name=name)
    elif type == "JoinLane":
        number = data["number"] if "number" in data else 2
        side = data["side"] if "side" in data else "right"
        return JoinLane(number, annotations, side=sideMap[side], name=name)
    else:
        print "Unsupported lane type: %s"% type
    return None

def readGraph(data):
    # graph has nodes, edges, roads
    g = Graph()
    for n in data["nodes"]:
        g.addNode(position=Position(n["x"], n["y"]), name=(n["name"] if "name" in n else None))
    for e in data["edges"]:
        start = g.nodeNames[e["start"]]
        end = g.nodeNames[e["end"]]
        g.addEdge(start, end, name=(e["name"] if "name" in e else None))
    for r in data["roads"]:
        alongEdge = g.edgeNames[r["alongEdge"]]
        ways = map(lambda w: readWay(w), r["ways"])
        annotations = map(lambda w: readAnnotation(w), r["annotations"])
        road = Road(alongEdge=alongEdge, ways=ways, annotations=annotations, name=(r["name"] if "name" in r else None))
        g.addRoad(road)
    return g


# Insert comment here...
class Graph(object):
    __slots__ = ['nodes', 'edges', 'roads', 'nodeNames', 'edgeNames', 'roadNames']

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.roads = []
        self.nodeNames = {}
        self.edgeNames = {}
        self.roadNames = {}

    def __repr__(self):
        return 'Graph'

    def addNode(self, position, name=None):
        node = Node(position=position, name=name)
        self.nodes.append(node)
        if node.name:
            self.nodeNames[node.name] = node
        return node

    def addEdge(self, start, end, name=None):
        edge = Edge(start=start, end=end, name=name)
        self.edges.append(edge)
        start.neighbors.append(end)
        end.neighbors.append(start)
        if edge.name:
            self.edgeNames[edge.name] = edge
        return edge

    def addRoad(self, road):
        self.roads.append(road)
        if road.name:
            self.roadNames[road.name] = road
        return road


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
    __slots__ = ['position', 'neighbors', 'name']

    def __init__(self, position=Position(0,0), name=None):
        self.position = position
        self.name = name
        self.neighbors = []

    def __repr__(self):
        return 'Node(position=%s, name=%s)' % (str(self.position), str(self.name))


# Insert comment here...
class Edge(object):
    __slots__ = ['start', 'end', 'name']

    def __init__(self, start=None, end=None, name=None):
        self.name = name
        self.start = start
        self.end = end

    def __repr__(self):
        return 'Edge(start=%s, end=%s, name=%s)' % (str(self.start), str(self.end),  str(self.name))

    def length(self):
        return self.start.position.vec2d().get_distance(self.end.position.vec2d())


# Insert comment here...
class Road(object):
    __slots__ = ['alongEdge', 'ways', 'annotations', 'name']

    def __init__(self, alongEdge=None, ways=[], annotations=[], name=None):
        self.alongEdge = alongEdge
        self.ways = ways
        self.name = name
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
    __slots__ = ['reversed', 'segments', 'annotations', 'name']

    def __init__(self, reversed=False, segments=[], annotations=[], name=None):
        self.reversed = reversed
        self.segments = segments
        self.name = name
        self.annotations = annotations

    def __repr__(self):
        return 'Way'


# Insert comment here...
class WaySegment(object):
    __slots__ = ['length', 'annotations', 'lanes', 'name']

    def __init__(self, length=None, annotations=[], lanes=[], name=None):
        self.length = length
        self.name = name
        self.annotations = annotations
        self.lanes = lanes

    def __repr__(self):
        return 'WaySegment'


# Insert comment here...
class Lane(object):
    __slots__ = ['annotations', 'type', 'name']

    def __init__(self, type, annotations=[], name=None):
        self.annotations = annotations
        self.name = name
        self.type = type

    def __repr__(self):
        return 'Lane'


# Insert comment here...
class BasicLane(Lane):
    __slots__ = ['width']

    def __init__(self, width=3.0, annotations=[], name=None):
        super(BasicLane, self).__init__(annotations=annotations, type="basic", name=name)
        self.width = width
        self.annotations = annotations

    def __repr__(self):
        return 'BasicLane'


class AnnotationSide:
    Center, Left, Right = range(3)

# lane will split into multiple lanes
class SplitLane(Lane):
    __slots__ = ['number', 'side']

    def __init__(self, number=2, annotations=[], side=AnnotationSide.Right, name=None):
        super(SplitLane, self).__init__(annotations=annotations, type="split", name=name)
        self.number = number
        self.side = side

    def __repr__(self):
        return 'SplitLane'


# several neighboring lanes will merge into one
class JoinLane(Lane):
    __slots__ = ['number', 'side']

    def __init__(self, number=2, annotations=[], side=AnnotationSide.Right, name=None):
        super(JoinLane, self).__init__(annotations=annotations, type="join", name=name)
        self.number = number
        self.annotations = annotations
        self.side = side

    def __repr__(self):
        return 'JoinLane'




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


class Sign(WayAnnotation):
    __slots__ = ['name']

    def __init__(self, name, position=None, side=AnnotationSide.Right):
        super(Sign, self).__init__(position=position, side=side)
        self.name = name

    def __repr__(self):
        return 'Sign'


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


class Crossing(WayAnnotation):
    __slots__ = ['width']

    def __init__(self, position=None, width=5.0):
        super(Crossing, self).__init__(position=position)
        self.width = width

    def __repr__(self):
        return 'Crossing'

class TrafficLightType:
    Normal, Pedestrian = range(2)


class TrafficLight(WayAnnotation):
    __slots__ = ['type', 'orientation']

    def __init__(self, position=None, side=AnnotationSide.Right, type=TrafficLightType.Normal, orientation=0.0):
        super(TrafficLight, self).__init__(position=position, side=side)
        self.type = type
        self.orientation = orientation

    def __repr__(self):
        return 'TrafficLight'
