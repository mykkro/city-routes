import os, sys

from cityroutes import cityroutes as cr



pa = cr.Position(100, 30)
pb = cr.Position(480, 370)

gr = cr.Graph()
na = gr.addNode(position=pa)
nb = gr.addNode(position=pb)
e1 = gr.addEdge(start=na, end=nb)


r1 = cr.Road(alongEdge=e1, ways=[
    cr.Way(segments=[
        cr.WaySegment(length=150, lanes=[
            cr.BasicLane(width=3.0, annotations=[

            ]),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
            cr.ParkingStripForward(length=50, position=20, side=cr.AnnotationSide.Right, boxAngle=90, boxLength=5, boxWidth=3)
        ]),
        cr.WaySegment(length=20, lanes=[
            cr.SplitLane(number=2),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
        ]),
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[
            ]),
            cr.BasicLane(width=3.0, annotations=[
            ]),
            cr.BasicLane(width=3.0, annotations=[

            ])
        ], annotations=[
        ])
    ]),
    cr.Way(reversed=True, segments=[
        cr.WaySegment(lanes=[
            cr.BasicLane(width=3.0, annotations=[
                # lane annotations go here...
            ])
        ], annotations=[
            cr.ParkingStripParallel(width=2.5, length=80, position=30)
        ])
    ])
])

from roadmeshgen.Vec2d import Vec2d
import os, sys, json
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier
from svg.path import parse_path
import svgwrite


class CityRoutesSVGGenerator:
    def __init__(self):
        self.dwg = svgwrite.Drawing('test.svg', profile='tiny', size=(1000, 1000))

    def test(self):
        self.dwg.add(self.dwg.line((0, 0), (1000, 1000), stroke=svgwrite.rgb(10, 10, 16, '%')))
        self.dwg.add(self.dwg.text('Test', insert=(200, 100), fill='red'))

    def save(self):
        self.dwg.save()

    def color(self, r, g, b):
        return svgwrite.rgb(r, g, b, '%')

    def grid(self):
        col = svgwrite.rgb(80, 80, 80, '%')
        for i in range(0, 100):
            self.dwg.add(self.dwg.line((i*10, 0), (i*10, 1000), stroke=col))
            self.dwg.add(self.dwg.line((0, i*10), (1000, i*10), stroke=col))

    def bigpoint(self, vec, radius=5):
        self.dwg.add(self.dwg.circle((vec.x, vec.y), radius, fill=svgwrite.rgb(0,0,0, '%')))

    def line(self, start, end, color):
        self.dwg.add(self.dwg.line((start.x, start.y), (end.x, end.y), stroke=color))

    def rect(self, pos, size, color):
        self.dwg.add(self.dwg.rect((pos.x, pos.y), (size.x, size.y), fill=color))

    def edge(self, edge):
        start = edge.start.position.vec2d()
        end = edge.end.position.vec2d()
        self.node(edge.start)
        self.node(edge.end)
        self.line(start, end, self.color(80, 80, 70))

    def node(self, node):
        self.bigpoint(node.position.vec2d())

csvg = CityRoutesSVGGenerator()
csvg.grid()

csvg.edge(r1.alongEdge)

# TODO: LaneGraph
class LaneNode(object):
    __slots__ = ['inLanes', 'inWidth', 'outLanes', 'outWidth', 'lane']

    def __init__(self, lane):
        self.inLanes = []
        self.outLanes = []
        self.inWidth = None
        self.outWidth = None
        self.lane = lane

# draw Road
roadLen = r1.length()
yy = 300
csvg.rect(Vec2d(0, yy), Vec2d(roadLen, 10), csvg.color(100, 50, 50))
yy += 20
# draw Ways
ways = r1.ways
for way in ways:
    csvg.rect(Vec2d(0, yy), Vec2d(roadLen, 10), csvg.color(50, 100, 50))
    yy += 15
    # draw Segments
    segLenTotal = 0
    ndx = 0
    slns = []
    for seg in way.segments:
        rest = roadLen - segLenTotal
        segLength = seg.length or rest
        print way.reversed, seg.length, segLength
        x1 = segLenTotal
        x2 = segLenTotal + segLength
        csvg.rect(Vec2d(x1, yy), Vec2d(x2-x1, 8), csvg.color(50, ndx*40, 50))

        lns = []
        lndx = 0
        for lane in seg.lanes:
            print lane, lane.type
            ln = LaneNode(lane)
            lns.append(ln)
            lndx += 1
        slns.append(lns)
        ndx += 1
        segLenTotal += segLength
    yy += 15

    # connect lane nodes into lane graph
    for i in range(0, len(slns)-1):
        curr = slns[i]
        next = slns[i+1]
        # zip them together...
        print len(curr), len(next)
        cind = 0
        nind = 0
        while cind < len(curr):
            cc = curr[cind]
            nn = next[nind]
            if cc.lane.type == "basic":
                if nn.lane.type == "basic" or nn.lane.type == "split":
                    # connect basic - basic
                    cc.outLanes = [nn]
                    nn.inLanes = [cc]
                    cind += 1
                    nind += 1
                elif nn.lane.type == "join":
                    print "Not implemented yet!"
            elif cc.lane.type == "split":
                num = cc.lane.number
                for k in range(0, num):
                    cc.outLanes.append(next[nind+k])
                    next[nind+k].inLanes = [cc]
                cind += 1
                nind += num
            else:
                print "Not implemented yet!"

    # compute start and end widths
    for i in range(0, len(slns)):
        curr = slns[i]
        for cc in curr:
            if cc.lane.type == "basic":
                cc.inWidth = cc.outWidth = cc.lane.width

    for i in range(1, len(slns)-1):
        curr = slns[i]
        for cc in curr:
            if cc.lane.type == "split" or cc.lane.type == "join":
                inWidth = 0
                outWidth = 0
                for cl in cc.inLanes:
                    inWidth += cl.outWidth
                for cl in cc.outLanes:
                    outWidth += cl.inWidth
                cc.inWidth = inWidth
                cc.outWidth = outWidth

    # print it!
    nnndx = 0
    for col in slns:
        print "Segment #%d" % nnndx
        for node in col:
            print node.lane.type, node.inWidth, node.outWidth, len(node.inLanes), len(node.outLanes)
        nnndx += 1
        print

csvg.save()


print r1, r1.length()
print r1.explain()