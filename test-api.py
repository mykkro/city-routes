import os, sys
from cityroutes import cityroutes as cr
import random
from roadmeshgen.Vec2d import Vec2d
from cityroutes.Border import Border
import os, sys, json
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier
from svg.path import parse_path
import svgwrite


pa = cr.Position(100, 330)
pb = cr.Position(480, 670)

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


from cityroutes.CityRoutesSVGGenerator import CityRoutesSVGGenerator

csvg = CityRoutesSVGGenerator()
csvg.grid()

csvg.edge(r1.alongEdge)

# TODO: LaneGraph
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
        return Border([Vec2d(0, self.inOffset * 10), Vec2d(self.length(), self.outOffset * 10)])

    def rightBorder(self):
        return Border([Vec2d(0, (self.inOffset+self.inWidth)*10), Vec2d(self.length(), (self.outOffset+self.outWidth)*10)])

    def body(self):
        return Border([Vec2d(0, self.inWidth*10), Vec2d(self.length(), self.outWidth*10)])


def transformPoint(p, origin=Vec2d(0,0), xaxis=Vec2d(1,0), yaxis=Vec2d(0,1)):
    return origin + xaxis*p.x + yaxis*p.y


def renderQuad(p1, p2, p3, p4, origin=Vec2d(0,0), xaxis=Vec2d(1,0), yaxis=Vec2d(0,1), color=None):
    t1 = transformPoint(p1, origin, xaxis, yaxis)
    t2 = transformPoint(p2, origin, xaxis, yaxis)
    t3 = transformPoint(p3, origin, xaxis, yaxis)
    t4 = transformPoint(p4, origin, xaxis, yaxis)
    return csvg.path([t1, t2, t3, t4], color or csvg.color(0,0,0))


# draw Road
roadLen = r1.length()
yy = 300
csvg.rect(Vec2d(0, yy), Vec2d(roadLen, 10), csvg.color(100, 50, 50))
yy += 20
# draw Ways
ways = r1.ways
wayNodes = []
for way in ways:
    wayNode = WayNode(way)
    wayNodes.append(wayNode)
    csvg.rect(Vec2d(0, yy), Vec2d(roadLen, 10), csvg.color(50, 100, 50))
    yy += 15
    # draw Segments
    segLenTotal = 0
    segNodes = []
    for seg in way.segments:
        rest = roadLen - segLenTotal
        segLength = seg.length or rest
        segNode = SegNode(seg=seg, segLength=segLength, segStart=segLenTotal)
        segNodes.append(segNode)
        wayNode.segments.append(segNode)
        x1 = segLenTotal
        x2 = segLenTotal + segLength
        csvg.rect(Vec2d(x1, yy), Vec2d(x2-x1, 8), csvg.randomcolor())

        for lane in seg.lanes:
            print lane, lane.type
            ln = LaneNode(lane, segNode)
            segNode.lanes.append(ln)

        segLenTotal += segLength
    yy += 15

    # connect lane nodes into lane graph
    for i in range(0, len(segNodes)-1):
        curr = segNodes[i].lanes
        next = segNodes[i+1].lanes
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
    for i in range(0, len(segNodes)):
        curr = segNodes[i].lanes
        for cc in curr:
            if cc.lane.type == "basic":
                cc.inWidth = cc.outWidth = cc.lane.width

    for i in range(1, len(segNodes)-1):
        curr = segNodes[i].lanes
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

    # connect segments
    for i in range(0, len(segNodes)-1):
        segNodes[i].outSegment = segNodes[i+1]
        segNodes[i+1].inSegment = segNodes[i]

    # render way
    y00 = 100
    for wn in wayNodes:
        x0 = 0
        for sn in wn.segments:
            y0 = 0
            y1 = 0
            x1 = x0 + sn.segLength
            w0 = sn.inWidth() * 10
            w1 = sn.outWidth() * 10
            print x0, x1, w0, w1
            csvg.path([Vec2d(x0, y0+y00), Vec2d(x1, y1+y00), Vec2d(x1, y1+w1+y00), Vec2d(x0, y0+w0+y00)], csvg.randomcolor())
            x0 = x1
        y00 += 100


pa = pa.vec2d()
pb = pb.vec2d()
xvec = (pb - pa).normalized()
yvec = xvec.perpendicular()

csvg.line(pa, pb, csvg.color(0,0,0))
csvg.arrowpoint(pa, xvec)
csvg.arrowpoint(pa, yvec)


origin = pa
xaxis = xvec
yaxis = yvec

def drawBorder(bb, color=None, origin=Vec2d(0,0), xaxis=Vec2d(1,0), yaxis=Vec2d(0,1)):
    color = color or csvg.color(0,0,0)
    for pt in bb.points:
        csvg.bigpoint(transformPoint(pt, origin, xaxis, yaxis))
    for i in range(0, len(bb.points)-1):
        startpt = bb.points[i]
        endpt = bb.points[i+1]
        csvg.line(transformPoint(startpt, origin, xaxis, yaxis), transformPoint(endpt, origin, xaxis, yaxis), color)


for j in range(0, len(wayNodes)):
    way = wayNodes[j]

    if way.way.reversed:
        origin = pb
        xaxis = -xvec
        yaxis = -yvec
    else:
        origin = pa
        xaxis = xvec
        yaxis = yvec
    x = 0
    ndx = 0
    if len(wayNodes) == 1:
        offsets = map(lambda x: -x/2, way.widths())
    else:
        offsets = [0] * (len(way.segments) + 1)

    for i in range(0, len(way.segments)):
        segment = way.segments[i]
        print "Segment:", segment, segment.segLength
        dseg = segment.segLength
        iw = segment.inWidth()
        ow = segment.outWidth()
        inOffset = offsets[i]
        outOffset = offsets[i+1]
        segment.inOffset = inOffset
        segment.outOffset = outOffset
        renderQuad(Vec2d(x, inOffset*10), Vec2d(x, (iw+inOffset)*10), Vec2d(x+dseg, (ow+outOffset)*10), Vec2d(x+dseg, outOffset*10), origin, xaxis, yaxis, csvg.color(100, ndx * 20, 0))

        for lane in segment.lanes:
            print lane, lane.inWidth, lane.outWidth
            iw = lane.inWidth
            ow = lane.outWidth
            renderQuad(Vec2d(x, inOffset*10), Vec2d(x, (iw+inOffset)*10), Vec2d(x+dseg, (ow+outOffset)*10), Vec2d(x+dseg, outOffset*10), origin, xaxis, yaxis, csvg.color(ndx * 20, 0, 100))
            lane.inOffset = inOffset
            lane.outOffset = outOffset

            #oo = origin + xaxis * lane.start()
            #drawBorder(lane.rightBorder(), color=None, origin=oo, xaxis=xaxis, yaxis=yaxis)

            inOffset += iw
            outOffset += ow
        x += segment.segLength
        ndx += 1

        #oo = origin + xaxis * segment.segStart
        #drawBorder(segment.rightBorder(), color=None, origin=oo, xaxis=xaxis, yaxis=yaxis)

    drawBorder(way.rightBorder(), color=None, origin=origin, xaxis=xaxis, yaxis=yaxis)


# simple Border API



bb = Border([Vec2d(0, 30), Vec2d(20, 40), Vec2d(35, 45), Vec2d(45, 30), Vec2d(50, 20)])
bb2 = Border([Vec2d(0, 20), Vec2d(30, 20), Vec2d(50, 10)])


drawBorder(bb, csvg.color(0,100,0))
drawBorder(bb2, csvg.color(0,50,0))

bb3 = bb.join(bb2, add=False)
bb4 = bb3.join(bb2, add=True)
print bb.points
print bb2.points
print bb3.points
print bb4.points

bb5 = Border.merge([bb, bb2])
print bb5.points

drawBorder(bb3, csvg.color(0,0,0))
drawBorder(bb4.flipped(), csvg.color(50,0,0))
drawBorder(bb5, csvg.color(50,0,0))

csvg.save()



print r1, r1.length()
print r1.explain()