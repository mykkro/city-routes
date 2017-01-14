from Vec2d import Vec2d
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier
from OPoint2d import OPoint2d

def makePoint(dwg, p, point_size=5, point_color="black"):
    return dwg.circle((p.x, p.y), point_size, fill=point_color)


def makeCircle(dwg, p, radius, fill="none", stroke="black"):
    return dwg.circle((p.x, p.y), radius, fill=fill, stroke=stroke)


def getCirclePath(cx, cy, r):
    return "M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0" % (cx-r, cy, r, r, 2*r, r, r, -2*r)


def makeOPoint(dwg, op, point_size=5, point_color="black", arrow_length=20):
    disp = op.v.normalized() * arrow_length
    group = dwg.g()
    group.add(dwg.circle((op.p.x, op.p.y), point_size, fill=point_color))
    group.add(dwg.line((op.p.x, op.p.y),(op.p.x+disp.x, op.p.y+disp.y), stroke=point_color, stroke_width=point_size))
    return group


def makeHalfline(dwg, op, l=1000, color="black"):
    disp = op.v.normalized() * l
    return dwg.line((op.p.x, op.p.y),(op.p.x+disp.x, op.p.y+disp.y), stroke=color)



def makeArcPathSegment(a, b, l=None):
    dist = a.p.get_distance(b.p)
    if l is None:
        l = dist*0.4
    p0 = Vec2d(a.p.x, a.p.y)
    p1 = Vec2d(a.p.x+a.v.x*l, a.p.y+a.v.y*l)
    p2 = Vec2d(b.p.x-b.v.x*l, b.p.y-b.v.y*l)
    p3 = Vec2d(b.p.x, b.p.y)
    return CubicBezier(complex(p0.x, p0.y), complex(p1.x, p1.y), complex(p2.x, p2.y), complex(p3.x, p3.y))


def makeArc(dwg, a, b, l=None, arc_color="black"):
    path = Path(makeArcPathSegment(a, b, l))
    return dwg.path(path.d(), fill="none", stroke=arc_color)


def makeTriangle(dwg, a, b, c, stroke="black", fill="none"):
    A = complex(a.x, a.y)
    B = complex(b.x, b.y)
    C = complex(c.x, c.y)
    path = Path(Line(A,B), Line(B, C), Line(C, A))
    return dwg.path(path.d(), stroke=stroke, fill=fill)


# sample points along the path
def makePathPoints(segment, min_dist=60):
    total_length = segment.length(error=1e-5)
    n = int(total_length / min_dist)
    if n < 1:
        n = 1
    points = []
    for i in range(0, n+1):
        ratio = float(i)/n
        pt = segment.point(ratio)
        points.append(Vec2d(pt.real, pt.imag))
    return points


def makePathVectors(a, b, path, min_dist=60):
    pts = makePathPoints(path, min_dist)
    vecs = [ None ] * len(pts)
    for i in range(0, len(pts)):
        if i == 0:
            vecs[i] = a
        elif i == len(pts)-1:
            vecs[i] = b
        else:
            pt = pts[i]
            ptprev = pts[i-1]
            ptnext = pts[i+1]
            v1 = (pt - ptprev).normalized()
            v2 = (ptnext - pt).normalized()
            v = v1+v2
            vecs[i] = OPoint2d(pt, v)
    return vecs


def getArcLength(a, b):
    segment = Path(makeArcPathSegment(a, b))
    return segment.length(error=1e-5)


def getArcPoint(a, b, dist=0, relative=False):
    segment = Path(makeArcPathSegment(a, b))
    if relative:
        ratio = dist
    else:
        len = segment.length(error=1e-5)
        ratio = dist/len
    pt = segment.point(ratio)
    return Vec2d(pt.real, pt.imag)


def getArcVector(a, b, dist=0, delta=1.0):
    segment = Path(makeArcPathSegment(a, b))
    len = segment.length(error=1e-5)
    ratio = dist/len
    pt = segment.point(ratio)
    if dist < delta:
        ratio2 = (dist+delta)/len
        pt2 = segment.point(ratio2)
        v = pt2 - pt
    elif dist+delta > len:
        ratio1 = (dist-delta)/len
        pt1 = segment.point(ratio1)
        v = pt - pt1
    else:
        ratio1 = (dist-delta)/len
        ratio2 = (dist+delta)/len
        pt1 = segment.point(ratio1)
        pt2 = segment.point(ratio2)
        v = (pt-pt1) + (pt2-pt)
    return OPoint2d(Vec2d(pt.real, pt.imag), Vec2d(v.real, v.imag))


def makeArcVectors(a, b, l=None, min_dist=60):
    path = Path(makeArcPathSegment(a, b, l))
    pts = makePathPoints(path, min_dist)
    vecs = [ None ] * len(pts)
    for i in range(0, len(pts)):
        if i == 0:
            vecs[i] = a
        elif i == len(pts)-1:
            vecs[i] = b
        else:
            pt = pts[i]
            ptprev = pts[i-1]
            ptnext = pts[i+1]
            v1 = pt - ptprev
            v2 = ptnext - pt
            v = v1+v2
            vecs[i] = OPoint2d(pt, v)
    return vecs


def drawMesh(dwg, mesh):
    for tri in mesh.triangles:
        dwg.add(makeTriangle(dwg, mesh.vertices[tri[0]], mesh.vertices[tri[1]], mesh.vertices[tri[2]]))


def getOffsetPath(vecseq, offset, endOffset=None):
    o1 = offset
    o2 = endOffset if endOffset is not None else offset
    n = len(vecseq)
    out = [None] * n
    for i in range(0, n):
        pt = vecseq[i]
        off = o1 + (o2-o1)*i/(n-1)
        out[i] = Vec2d(pt.p + (off * pt.v.perpendicular()))
    return out
