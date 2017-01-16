import json
from cityroutes import cityroutes as cr
from cityroutes.cityroutes import AnnotationSide
from roadmeshgen.Vec2d import Vec2d
from cityroutes.Border import Border
from cityroutes.CityRoutesSVGGenerator import CityRoutesSVGGenerator




path = "media/samples/sample.json"
with open(path, "rb") as infile:
    data = json.load(infile)
    graph = cr.readGraph(data)
    r1 = graph.roads[0]



csvg = CityRoutesSVGGenerator()
csvg.grid()


# TODO: LaneGraph

from cityroutes.street import LaneNode, SegNode, WayNode, RoadNode

# draw Road
roadLen = r1.length()
# draw Ways
ways = r1.ways
road = RoadNode(r1)
for way in ways:
    wayNode = WayNode(way)
    road.ways.append(wayNode)
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
        for lane in seg.lanes:
            ln = LaneNode(lane, segNode)
            segNode.lanes.append(ln)
        segLenTotal += segLength

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
            if cc.lane.type == "basic" or cc.lane.type == "join":
                if nn.lane.type == "basic" or nn.lane.type == "split":
                    # connect basic - basic
                    cc.outLanes = [nn]
                    nn.inLanes = [cc]
                    cind += 1
                    nind += 1
                elif nn.lane.type == "join":
                    num = nn.lane.number
                    for k in range(0, num):
                        nn.inLanes.append(curr[cind+k])
                        curr[cind+k].outLanes = [nn]
                    nind += 1
                    cind += num
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



pa = r1.alongEdge.start.position.vec2d()
pb = r1.alongEdge.end.position.vec2d()
xvec = (pb - pa).normalized()
yvec = xvec.perpendicular()

origin = pa
xaxis = xvec
yaxis = yvec


def placeSign(ann, bl, br, oo, xaxis, yaxis):
    if ann.side == AnnotationSide.Right:
        signx = ann.position
        signy = br.width(signx)
        signy += 2
    elif ann.side == AnnotationSide.Left:
        signx = ann.position
        signy = bl.width(signx)
        signy -= 2
    else:
        signx = ann.position
        signy = (bl.width(signx) + br.width(signx))/2
    pt = csvg.transformPoint(Vec2d(signx, signy), oo, xaxis, yaxis)
    csvg.sign(ann.name, (pt.x, pt.y))


def placeTrafficLight(ann, bl, br, oo, xaxis, yaxis):
    if ann.side == AnnotationSide.Right:
        signx = ann.position
        signy = br.width(signx)
        signy += 2
    elif ann.side == AnnotationSide.Left:
        signx = ann.position
        signy = bl.width(signx)
        signy -= 2
    else:
        signx = ann.position
        signy = (bl.width(signx) + br.width(signx))/2
    pt = csvg.transformPoint(Vec2d(signx, signy), oo, xaxis, yaxis)
    csvg.trafficLight((pt.x, pt.y))


for j in range(0, len(road.ways)):
    way = road.ways[j]

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
    if len(road.ways) == 1:
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
        csvg.quad(Vec2d(x, inOffset), Vec2d(x, (iw+inOffset)), Vec2d(x+dseg, (ow+outOffset)), Vec2d(x+dseg, outOffset), origin, xaxis, yaxis, csvg.color(100, ndx * 20, 0))

        for lane in segment.lanes:
            print lane, lane.inWidth, lane.outWidth
            iw = lane.inWidth
            ow = lane.outWidth
            csvg.quad(Vec2d(x, inOffset), Vec2d(x, (iw+inOffset)), Vec2d(x+dseg, (ow+outOffset)), Vec2d(x+dseg, outOffset), origin, xaxis, yaxis, csvg.color(ndx * 20, 0, 100))
            lane.inOffset = inOffset
            lane.outOffset = outOffset

            #oo = origin + xaxis * lane.start()
            #drawBorder(lane.rightBorder(), color=None, origin=oo, xaxis=xaxis, yaxis=yaxis)

            inOffset += iw
            outOffset += ow

        br = segment.rightBorder()
        bl = segment.leftBorder()
        oo = origin + xaxis * segment.segStart


        for ann in segment.segment.annotations:
            print "Segment annotation", ann
            if isinstance(ann, cr.Sign):
                placeSign(ann, bl, br, oo, xaxis, yaxis)
            elif isinstance(ann, cr.TrafficLight):
                placeTrafficLight(ann, bl, br, oo, xaxis, yaxis)

        x += segment.segLength
        ndx += 1

        #drawBorder(segment.rightBorder(), color=None, origin=oo, xaxis=xaxis, yaxis=yaxis)

    br = way.rightBorder()
    bl = way.leftBorder()

    for ann in way.way.annotations:
        print "Way annotation", ann
        if isinstance(ann, cr.Sign):
            placeSign(ann, bl, br, origin, xaxis, yaxis)
        elif isinstance(ann, cr.TrafficLight):
            placeTrafficLight(ann, bl, br, oo, xaxis, yaxis)


    # csvg.border(way.rightBorder(), color=None, origin=origin, xaxis=xaxis, yaxis=yaxis)


br = road.rightBorder()
bl = road.leftBorder()

for ann in road.road.annotations:
    print "Road annotation", ann
    if isinstance(ann, cr.Crossing):
        print ann.position, ann.width
        stripeWidth = 1.0
        cx = ann.position
        ymin = bl.width(cx)
        ymax = br.width(cx)
        y = ymin
        while y < ymax:
            p0 = Vec2d(cx - ann.width/2, y)
            p1 = Vec2d(cx + ann.width/2, y)
            p2 = Vec2d(cx + ann.width/2, y+stripeWidth)
            p3 = Vec2d(cx - ann.width/2, y+stripeWidth)
            csvg.quad(p0, p1, p2, p3, pa, xvec, yvec, color=csvg.color(100, 100, 100))
            y += 2*stripeWidth

csvg.border(br, color=None, origin=pa, xaxis=xvec, yaxis=yvec)
csvg.border(bl, color=None, origin=pa, xaxis=xvec, yaxis=yvec)

csvg.save()



print r1, r1.length()
print r1.explain()