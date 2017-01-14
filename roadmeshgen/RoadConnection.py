from Vec2d import Vec2d
from MeshBuilder import MeshBuilder, Mesh
from OPoint2d import OPoint2d
from svgpathutil import makeArcVectors, makeOPoint, makePoint, makeCircle
from geom import checkLineIntersection, circleHalfLineIntersection, circleIntersection
from roadmarker import RoadMarker
from RoadSegment import RoadSegment


class RoadConnection(object):
    __slots__ = ['A', 'B', 'C', 'minRadius', 'widthA', 'widthC', 'offsetA', 'offsetC', 'nameA', 'nameC', 'vecA', 'vecC',  'minDist', 'outerBorder', 'innerBorder']

    def __init__(self, A, B, C, widthA, widthC, offsetA, offsetC, nameA, nameC, minRadius=5, minDist=1, innerBorder=1, outerBorder=1):
        self.A = A
        self.B = B
        self.C = C
        self.widthA = widthA
        self.widthC = widthC
        self.offsetA = offsetA
        self.offsetC = offsetC
        self.nameA = nameA
        self.nameC = nameC
        self.minRadius = minRadius
        self.vecA = None
        self.vecC = None
        self.minDist = minDist
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder

    def __repr__(self):
        return 'RoadConnection(A=%s, B=%s, C=%s)' % (self.A, self.B, self.C)

    def getExit(self, name):
        if name == self.nameA:
            return {
                "name": self.nameA,
                "vec": self.vecA,
                "width": self.widthA,
                "offset": self.offsetA
            }
        if name == self.nameC:
            return {
                "name": self.nameC,
                "vec": self.vecC,
                "width": self.widthC,
                "offset": self.offsetC
            }
        return None

    def createMesh(self):
        A = self.A
        B = self.B
        C = self.C
        minRadius = self.minRadius

        # make normalized vectors C-B, A-B
        vc = (C-B).normalized()
        va = (A-B).normalized()
        v = (va + vc).normalized()

        # compute angle between vc and va
        angle = abs(va.get_angle_between(-vc))

        angleThreshold = 5.0
        if angle < angleThreshold:
            # if angle is too small - do not render mesh
            self.vecA = OPoint2d(B, (va-vc).normalized())
            self.vecC = OPoint2d(B, -self.vecA.v)
            return Mesh([], [])

        P = B + minRadius * v

        # Thales's circles
        PA = (A+P)/2
        ra = PA.get_distance(A)
        PC = (C+P)/2
        rc = PC.get_distance(C)

        interA = circleIntersection(P, PA, minRadius, ra)
        interC = circleIntersection(P, PC, minRadius, rc)

        # keep points on the opposite side
        u = P-A
        v = B-A
        w1 = interA[0]-A
        w2 = interA[1]-A
        s1 = u.x*v.y-u.y*v.x
        sw1 = u.x*w1.y-u.y*w1.x
        if(s1*sw1>0):
            IA = interA[0]
        else:
            IA = interA[1]

        u = P-C
        v = B-C
        w1 = interC[0]-C
        w2 = interC[1]-C
        s1 = u.x*v.y-u.y*v.x
        sw1 = u.x*w1.y-u.y*w1.x
        if(s1*sw1>0):
            IC = interC[0]
        else:
            IC = interC[1]

        va = (A-IA).normalized()
        VA = OPoint2d(IA, va)
        vc = (C-IC).normalized()
        VC = OPoint2d(IC, vc)

        self.vecA = VA
        self.vecC = VC

        ra = RoadMarker(VA, self.widthA, self.offsetA)
        rb = RoadMarker(VC, self.widthC, self.offsetC)
        rs = RoadSegment(ra.reversed(), rb, minDist=self.minDist, innerBorder=self.innerBorder, outerBorder=self.outerBorder)
        return rs.createMesh()


