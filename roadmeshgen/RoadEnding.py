from Vec2d import Vec2d
from meshxml import Mesh
from OPoint2d import OPoint2d
from svgpathutil import makeArcVectors
from Vec2d import Vec2d
from Vec3d import Vec3d
from Tex2d import Tex2d
from meshxml import Mesh
from OPoint2d import OPoint2d
from Vertex import Vertex


class RoadEnding(object):
    __slots__ = ['pos', 'minDist', 'innerBorder', 'outerBorder']

    def __init__(self, pos, minDist=1, innerBorder=1, outerBorder=1):
        self.pos = pos
        self.minDist = minDist
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder

    def createMesh(self):
        lstartoff = self.pos.leftOffset()
        rstartoff = self.pos.rightOffset()
        p0 = self.pos.pt.p
        v = self.pos.pt.v.perpendicular()
        pl = p0 + lstartoff * v
        pr = p0 + rstartoff * v
        A = OPoint2d(pl, self.pos.pt.v)
        B = OPoint2d(pr, -self.pos.pt.v)
        av = makeArcVectors(A, B, l=A.p.get_distance(B.p)*0.7, min_dist=self.minDist)
        n = len(av)
        pts = [None]*(3*n+1)
        for i in range(0, n):
            x = float(i)/3
            pt = av[i]
            pts[i] = Vertex(position=Vec3d(pt.p.x, pt.p.y, 0), normal=Vec3d(0,0,1), texcoord=Tex2d(x,0.75), tangent=None, colour_diffuse=None)
            pt2 = Vec2d(pt.p + (-self.innerBorder * pt.v.perpendicular()))
            pts[i+n] = Vertex(position=Vec3d(pt2.x, pt2.y, 0), normal=Vec3d(0,0,1), texcoord=Tex2d(x,0.84), tangent=None, colour_diffuse=None)
            pt3 = Vec2d(pt.p + (-(self.innerBorder + self.outerBorder) * pt.v.perpendicular()))
            pts[i+2*n] = Vertex(position=Vec3d(pt3.x, pt3.y, 0), normal=Vec3d(0,0,1), texcoord=Tex2d(x,1), tangent=None, colour_diffuse=None)
        pts[3*n] = Vertex(position=Vec3d(p0.x, p0.y, 0), normal=Vec3d(0,0,1), texcoord=Tex2d(x,0), tangent=None, colour_diffuse=None)

        tris = []
        for i in range(0, 2):
            for j in range(0, n-1):
                a = j+i*n
                b = j+1+i*n
                c = j+(i+1)*n
                d = j+1+(i+1)*n
                tris.append((a, c, b))
                tris.append((b, c, d))
        for j in range(0, n-1):
            a = j
            b = j+1
            c = 3*n
            tris.append((a, b, c))

        return Mesh(pts, tris)
