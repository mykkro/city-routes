import math
from svg.path import Path, Line, Arc
from MeshBuilder import MeshBuilder
from geom import checkLineIntersection
from svgpathutil import makePathVectors, getOffsetPath
from Vec2d import Vec2d
from Vec3d import Vec3d
from Tex2d import Tex2d
from OPoint2d import OPoint2d
from Vertex import Vertex


class RoadIntersection(object):
    __slots__ = ['center', 'names', 'directions', 'widths', 'offsets', 'rays', 'innerBorder', 'outerBorder', 'minRadius', 'minOuterGap', 'minDist']

    def __init__(self, center, names, directions, widths, offsets, innerBorder=1, outerBorder=1, minRadius=5, minOuterGap=1, minDist=1):
        self.center = center
        self.names = names
        self.directions = directions
        self.widths = widths
        self.offsets = offsets
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder
        self.minRadius = minRadius
        self.minOuterGap = minOuterGap
        self.minDist = minDist

    def getExit(self, name):
        for ray in self.rays:
            if ray["name"] == name:
                rr = ray
                break
        if rr is None:
            return None
        for i in range(0, len(self.names)):
            n = self.names[i]
            if n==name:
                return {
                    "name": n,
                    "vec": OPoint2d(rr["midEndPoint"], rr["ray"].v),
                    "width": self.widths[i],
                    "offset": self.offsets[i]
                }
        return None

    def createMesh(self):
        center = self.center
        directions = self.directions
        widths = self.widths
        offsets = self.offsets
        mb = MeshBuilder()
        minRadius = self.minRadius
        rays = [None] * len(directions)
        self.rays = rays
        for i in range(0, len(directions)):
            dir = directions[i].normalized()
            ray = OPoint2d(center, dir)
            vec = dir.perpendicular()
            leftOffset = -widths[i]/2 + offsets[i]
            rightOffset = widths[i]/2 + offsets[i]
            leftLine = OPoint2d(center + leftOffset*vec, dir)
            rightLine = OPoint2d(center + rightOffset*vec, dir)
            leftIntersectionLine = OPoint2d(center + (leftOffset-minRadius)*vec, dir)
            rightIntersectionLine = OPoint2d(center + (rightOffset+minRadius)*vec, dir)
            rays[i] = {
                "ray": ray,
                "name": self.names[i],
                "width": widths[i],
                "offset": offsets[i],
                "leftOffset": leftOffset,
                "rightOffset": rightOffset,
                "leftLine": leftLine,
                "rightLine": rightLine,
                "leftIntersectionLine": leftIntersectionLine,
                "rightIntersectionLine": rightIntersectionLine,
                "angle": math.atan2(ray.v.y, ray.v.x)
            }

        # 1. sort rays according to  increasing angle
        rays.sort(key=lambda x: x["angle"])

        # 2. find intersection between intersection lines
        n = len(rays)
        maxDist = 0
        for i in range(0, n):
            r1 = rays[i]
            r2 = rays[(i+1) % n]
            l1 = r1["rightIntersectionLine"]
            l2 = r2["leftIntersectionLine"]
            res = checkLineIntersection(l1.p.x, l1.p.y, l1.p.x+1000*l1.v.x, l1.p.y+1000*l1.v.y, l2.p.x, l2.p.y, l2.p.x+1000*l2.v.x, l2.p.y+1000*l2.v.y)
            intersection = Vec2d(res["x"], res["y"])
            r1["intersectionWithNext"] = intersection
            d1 = r1["rightIntersectionDistance"] = intersection.get_distance(l1.p)
            d2 = r2["leftIntersectionDistance"] = intersection.get_distance(l2.p)
            if d1 > maxDist:
                maxDist = d1
            if d2 > maxDist:
                maxDist = d2
            r1["rightArcPoint"] = r1["rightLine"].p + r1["rightLine"].v * r1["rightIntersectionDistance"]
            r2["leftArcPoint"] = r2["leftLine"].p + r2["leftLine"].v * r2["leftIntersectionDistance"]

        maxDist = maxDist + self.minOuterGap
        for i in range(0, n):
            r1 = rays[i]
            r1["rightEndPoint"] = r1["rightLine"].p + r1["rightLine"].v * maxDist
            r1["leftEndPoint"] = r1["leftLine"].p + r1["leftLine"].v * maxDist
            r1["midEndPoint"] = center + r1["leftLine"].v * maxDist

        norm = Vec3d(0,0,1)
        mb.addVertex("center", Vertex(position=Vec3d(center.x, center.y, 0), normal=norm, texcoord=Tex2d(0,0.1), tangent=None, colour_diffuse=None))
        arclengths = [None]*n
        raylengths = [None]*n

        for i in range(0, n):
            r1 = rays[i]
            r2 = rays[(i+1) % n]
            x = float(i)/3
            # draw arc paths
            z3 = r1["leftEndPoint"]
            a0 = r1["rightEndPoint"]
            a1 = r1["rightArcPoint"]
            a2 = r2["leftArcPoint"]
            a3 = r2["leftEndPoint"]

            line0 = Line(complex(z3.x, z3.y), complex(a0.x, a0.y))
            line1 = Line(complex(a0.x, a0.y), complex(a1.x, a1.y))
            arc = Arc(complex(a1.x, a1.y), complex(minRadius, minRadius), 0, 0, 0, complex(a2.x, a2.y))
            line2 = Line(complex(a2.x, a2.y), complex(a3.x, a3.y))

            r1["lineFromPrev"] = Path(line0)
            r1["arcToNext"] = Path(line1, arc, line2)

            minDist = self.minDist
            vecs = makePathVectors(OPoint2d(a0, -r1["ray"].v), OPoint2d(a3,r2["ray"].v), r1["arcToNext"], min_dist=minDist)
            r1["arcVecs"] = vecs

            # subdivide rays...
            m = int(maxDist/minDist)
            pts = [None]*(m-1)
            for j in range(0, m-1):
                x = float(j)/3
                pts[j] = center.interpolate_to(r1["midEndPoint"], float(j+1)/(m-1))
                mb.addVertex("ray%d%d" % (i, j), Vertex(position=Vec3d(pts[j].x, pts[j].y, 0), normal=norm, texcoord=Tex2d(x,0.1), tangent=None, colour_diffuse=None))
            raylengths[i] = m-1
            r1["rayPoints"] = pts

        for i in range(0, n):
            r1 = rays[i]

            averts = getOffsetPath(r1["arcVecs"], 0)
            averts1 = getOffsetPath(r1["arcVecs"], -self.innerBorder)
            averts2 = getOffsetPath(r1["arcVecs"], -(self.innerBorder+self.outerBorder))

            arclengths[i] = len(averts)
            r1lengths = raylengths[i]
            r2lengths = raylengths[(i+1) % n]

            for j in range(0, len(averts)):
                x = float(j)/3
                mb.addVertex("arc0%d%d" % (i,j), Vertex(position=Vec3d(averts[j].x, averts[j].y, 0), normal=norm, texcoord=Tex2d(x,0.75), tangent=None, colour_diffuse=None))
                mb.addVertex("arc1%d%d" % (i,j), Vertex(position=Vec3d(averts1[j].x, averts1[j].y, 0), normal=norm, texcoord=Tex2d(x,84), tangent=None, colour_diffuse=None))
                mb.addVertex("arc2%d%d" % (i,j), Vertex(position=Vec3d(averts2[j].x, averts2[j].y, 0), normal=norm, texcoord=Tex2d(x,1), tangent=None, colour_diffuse=None))

            for j in range(0, arclengths[i]-1):
                na = "arc0%d%d" % (i, j)
                nb = "arc0%d%d" % (i, j+1)
                nc = "arc1%d%d" % (i, j)
                nd = "arc1%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)
            for j in range(0, arclengths[i]-1):
                na = "arc1%d%d" % (i, j)
                nb = "arc1%d%d" % (i, j+1)
                nc = "arc2%d%d" % (i, j)
                nd = "arc2%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)

            anames = []
            for k in range(0, len(averts)):
                anames.append("arc0%d%d" % (i, k))
            bnames = []
            for k in range(r1lengths-1, -1, -1):
                bnames.append("ray%d%d" % (i, k))
            bnames.append("center")
            for k in range(0, r2lengths):
                bnames.append("ray%d%d" % (((i+1) % n), k))

            mb.stitchVertices(anames, bnames)

        return mb.getMesh()
