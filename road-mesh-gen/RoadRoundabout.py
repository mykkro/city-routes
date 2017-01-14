import math
from Vec2d import Vec2d
from svg.path import Path, Line, Arc
from MeshBuilder import MeshBuilder
from meshxml import Mesh
from geom import checkLineIntersection, circleHalfLineIntersection
from OPoint2d import OPoint2d
from svgpathutil import makePathVectors, getOffsetPath
from Vertex import Vertex
from Tex2d import Tex2d
from Vec3d import Vec3d


class RoadRoundabout(object):
    __slots__ = ['center', 'names', 'directions', 'widths', 'offsets', 'minInnerRadius', 'roadWidth', 'minTurnRadius', 'rays',  'innerBorder', 'outerBorder', 'minTurnRadius', 'minDist', 'outerGap']

    def __init__(self, center, names, directions, widths, offsets, minInnerRadius, roadWidth, innerBorder=1, outerBorder=1, minTurnRadius=5, minDist=1, outerGap=2):
        self.center = center
        self.names = names
        self.directions = directions
        self.widths = widths
        self.offsets = offsets
        self.minInnerRadius = minInnerRadius
        self.roadWidth = roadWidth
        self.minTurnRadius = minTurnRadius # min radius of road turn
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder
        self.minDist = minDist
        self.outerGap = outerGap


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
                    "vec": OPoint2d(rr["endPoint"], rr["ray"].v),
                    "width": self.widths[i],
                    "offset": self.offsets[i]
                }
        return None

    def computeRays(self):
        # compute rays
        rays = [None] * len(self.directions)
        self.rays = rays
        for i in range(0, len(self.directions)):
            dir = self.directions[i].normalized()
            ray = OPoint2d(self.center, dir)
            vec = dir.perpendicular()
            leftOffset = -self.widths[i]/2 + self.offsets[i]
            rightOffset = self.widths[i]/2 + self.offsets[i]
            leftLine = OPoint2d(self.center + leftOffset*vec, dir)
            rightLine = OPoint2d(self.center + rightOffset*vec, dir)
            leftIntersectionLine = OPoint2d(self.center + (leftOffset-self.minTurnRadius)*vec, dir)
            rightIntersectionLine = OPoint2d(self.center + (rightOffset+self.minTurnRadius)*vec, dir)
            rays[i] = {
                "ray": ray,
                "name": self.names[i],
                "width": self.widths[i],
                "offset": self.offsets[i],
                "leftOffset": leftOffset,
                "rightOffset": rightOffset,
                "leftLine": leftLine,
                "rightLine": rightLine,
                "leftIntersectionLine": leftIntersectionLine,
                "rightIntersectionLine": rightIntersectionLine,
                "angle": math.atan2(ray.v.y, ray.v.x)
            }
        rays.sort(key=lambda x: x["angle"])
        return rays

    def createMesh(self):
        mb = MeshBuilder()

        # compute rays
        rays = self.computeRays()

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

        maxDist = maxDist + self.outerGap/2
        outerRadius = maxDist
        innerRadius = outerRadius - self.roadWidth
        if innerRadius < self.minInnerRadius:
            innerRadius = self.minInnerRadius
            outerRadius = innerRadius + self.roadWidth

        intersectionRadius = outerRadius + self.minTurnRadius

        # find intersections between intersection lines and intersection circle
        maxADistance = 0
        for i in range(0, n):
            r1 = rays[i]
            lhline = r1["leftIntersectionLine"]
            ptleft = circleHalfLineIntersection(self.center.x, self.center.y, intersectionRadius, lhline.p.x, lhline.p.y, lhline.v.x, lhline.v.y)
            rhline = r1["rightIntersectionLine"]
            ptright = circleHalfLineIntersection(self.center.x, self.center.y, intersectionRadius, rhline.p.x, rhline.p.y, rhline.v.x, rhline.v.y)
            if ptleft is None or ptright is None:
                raise Exception("Intersection expected, none found!")

            # projections to intersection lines
            distleft = ptleft.get_distance(r1["leftLine"].p)
            leftA = r1["leftLine"].p + distleft * r1["leftLine"].v
            distright = ptright.get_distance(r1["rightLine"].p)
            rightA = r1["rightLine"].p + distright * r1["rightLine"].v
            leftB = self.center + (ptleft-self.center).normalized() * outerRadius
            rightB = self.center + (ptright-self.center).normalized() * outerRadius
            r1["leftA"] = leftA
            r1["rightA"] = rightA
            r1["leftB"] = leftB
            r1["rightB"] = rightB
            r1["leftC"] = ptleft
            r1["rightC"] = ptright
            aDist = leftA.get_distance(self.center)
            if maxADistance < aDist:
                maxADistance = aDist
            aDist = rightA.get_distance(self.center)
            if maxADistance < aDist:
                maxADistance = aDist

        maxADistance += self.outerGap
        for i in range(0, n):
            r1 = rays[i]
            r1["leftD"] = r1["leftLine"].p + maxADistance * r1["leftLine"].v
            r1["rightD"] = r1["rightLine"].p + maxADistance * r1["rightLine"].v
            r1["endPoint"] = r1["ray"].p + maxADistance * r1["ray"].v
            r1["endIntPoint"] = r1["ray"].p + innerRadius * r1["ray"].v

        outerarclengths = [None]*n
        innerarclengths = [None]*n
        crosslinelengths = [None]*n

        for i in range(0, n):
            r1 = rays[i]
            r2 = rays[(i+1) % n]
            # draw arc paths
            a0 = r1["rightD"]
            a1 = r1["rightA"]
            a2 = r1["rightB"]
            a3 = r2["leftB"]
            a4 = r2["leftA"]
            a5 = r2["leftD"]
            b0 = r2["rightD"]

            line1 = Line(complex(a0.x, a0.y), complex(a1.x, a1.y))
            arc = Arc(complex(a1.x, a1.y), complex(self.minTurnRadius, self.minTurnRadius), 0, 0, 0, complex(a2.x, a2.y))
            arc2 = Arc(complex(a2.x, a2.y), complex(outerRadius, outerRadius), 0, 0, 1, complex(a3.x, a3.y))
            arc3 = Arc(complex(a3.x, a3.y), complex(self.minTurnRadius, self.minTurnRadius), 0, 0, 0, complex(a4.x, a4.y))
            line2 = Line(complex(a4.x, a4.y), complex(a5.x, a5.y))
            line3 = Line(complex(a5.x, a5.y), complex(b0.x, b0.y))

            r1["arcToNext"] = Path(line1, arc, arc2, arc3, line2)
            r1["lineToNext"] = Path(line3)

            minDist = self.minDist
            r1["outerArcVecs"] = makePathVectors(OPoint2d(a0, -r1["ray"].v), OPoint2d(a5,r2["ray"].v), r1["arcToNext"], min_dist=minDist)

            path2 = Line(complex(r1["endPoint"].x, r1["endPoint"].y), complex(r1["endIntPoint"].x, r1["endIntPoint"].y))
            r1["crossVecs"] = makePathVectors(OPoint2d(r1["endPoint"], -r1["ray"].v), OPoint2d(r1["endIntPoint"], -r1["ray"].v), path2, min_dist=minDist)

            path3 = Arc(complex(r1["endIntPoint"].x, r1["endIntPoint"].y), complex(innerRadius, innerRadius), 0, 0, 1, complex(r2["endIntPoint"].x, r2["endIntPoint"].y))
            r1["innerArcVecs"] = makePathVectors(OPoint2d(r1["endIntPoint"], r1["ray"].v.perpendicular()), OPoint2d(r2["endIntPoint"], r2["ray"].v.perpendicular()), path3, min_dist=minDist)

            outerarclengths[i] = len(r1["outerArcVecs"])
            innerarclengths[i] = len(r1["innerArcVecs"])
            crosslinelengths[i] = len(r1["crossVecs"])

            norm = Vec3d(0,0,1)
            for j in range(0, outerarclengths[i]):
                x = float(j)/3
                p = r1["outerArcVecs"][j].p
                mb.addVertex("outerarc0%d%d" % (i,j), Vertex(position=Vec3d(p.x, p.y, 0), normal=norm, texcoord=Tex2d(x,0.75)))
            for j in range(0, innerarclengths[i]):
                x = float(j)/3
                p = r1["innerArcVecs"][j].p
                mb.addVertex("innerarc0%d%d" % (i,j), Vertex(position=Vec3d(p.x, p.y, 0), normal=norm, texcoord=Tex2d(x,0.0)))
            for j in range(0, crosslinelengths[i]):
                x = float(j)/3
                p = r1["crossVecs"][j].p
                mb.addVertex("cross0%d%d" % (i,j), Vertex(position=Vec3d(p.x, p.y, 0), normal=norm, texcoord=Tex2d(x,0.1)))

        for i in range(0, n):
            r1 = rays[i]
            r2 = rays[(i+1) % n]

            anames = []
            bnames = []
            for j in range(0, outerarclengths[i]):
                anames.append("outerarc0%d%d" % (i,j))
            for j in range(0, crosslinelengths[i]):
                bnames.append("cross0%d%d" % (i,j))
            for j in range(1, innerarclengths[i]-1):
                bnames.append("innerarc0%d%d" % (i,j))
            for j in range(crosslinelengths[(i+1)%n]-1,-1,-1):
                bnames.append("cross0%d%d" % ((i+1)%n,j))

            mb.stitchVertices(anames, bnames)

            averts1 = getOffsetPath(r1["outerArcVecs"], -self.innerBorder)
            averts2 = getOffsetPath(r1["outerArcVecs"], -(self.innerBorder + self.outerBorder))

            for j in range(0, outerarclengths[i]):
                x = float(j)/3
                mb.addVertex("outerarc1%d%d" % (i,j), Vertex(position=Vec3d(averts1[j].x, averts1[j].y, 0), normal=norm, texcoord=Tex2d(x,0.84)))
                mb.addVertex("outerarc2%d%d" % (i,j), Vertex(position=Vec3d(averts2[j].x, averts2[j].y, 0), normal=norm, texcoord=Tex2d(x,1)))

            for j in range(0, outerarclengths[i]-1):
                na = "outerarc0%d%d" % (i, j)
                nb = "outerarc0%d%d" % (i, j+1)
                nc = "outerarc1%d%d" % (i, j)
                nd = "outerarc1%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)
            for j in range(0, outerarclengths[i]-1):
                na = "outerarc1%d%d" % (i, j)
                nb = "outerarc1%d%d" % (i, j+1)
                nc = "outerarc2%d%d" % (i, j)
                nd = "outerarc2%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)

            averts1 = getOffsetPath(r1["innerArcVecs"], self.innerBorder)
            averts2 = getOffsetPath(r1["innerArcVecs"], (self.innerBorder+self.outerBorder))

            for j in range(0, innerarclengths[i]):
                x = float(j)/3
                mb.addVertex("innerarc1%d%d" % (i,j), Vertex(position=Vec3d(averts1[j].x, averts1[j].y, 0), normal=norm, texcoord=Tex2d(0,0.84)))
                mb.addVertex("innerarc2%d%d" % (i,j), Vertex(position=Vec3d(averts2[j].x, averts2[j].y, 0), normal=norm, texcoord=Tex2d(0,1)))

            for j in range(0, innerarclengths[i]-1):
                na = "innerarc0%d%d" % (i, j)
                nb = "innerarc0%d%d" % (i, j+1)
                nc = "innerarc1%d%d" % (i, j)
                nd = "innerarc1%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)
            for j in range(0, innerarclengths[i]-1):
                na = "innerarc1%d%d" % (i, j)
                nb = "innerarc1%d%d" % (i, j+1)
                nc = "innerarc2%d%d" % (i, j)
                nd = "innerarc2%d%d" % (i, j+1)
                mb.addTriangle(na, nc, nd)
                mb.addTriangle(na, nd, nb)

        return mb.getMesh()
