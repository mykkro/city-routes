from Vec2d import Vec2d
from Vec3d import Vec3d
from Tex2d import Tex2d
from meshxml import Mesh
from OPoint2d import OPoint2d
from Vertex import Vertex
from svgpathutil import makeArcVectors, getArcLength, getArcVector


class RoadSegment(object):
    __slots__ = ['start', 'end', 'axis', 'minDist', 'outerBorder', 'innerBorder']

    def __init__(self, start, end, minDist=1, innerBorder=1, outerBorder=1):
        self.start = start
        self.end = end
        self.minDist = minDist
        self.innerBorder = innerBorder
        self.outerBorder = outerBorder
        self.axis = makeArcVectors(start.pt, end.pt, min_dist=minDist)

    def __repr__(self):
        return 'RoadSegment(start=%s, end=%s)' % (self.start, self.end)

    def getOffsetAxis(self, offset, endOffset=None):
        o1 = offset
        o2 = endOffset if endOffset is not None else offset
        n = len(self.axis)
        out = [None] * n
        for i in range(0, n):
            pt = self.axis[i]
            off = o1 + (o2-o1)*i/(n-1)
            out[i] = Vec2d(pt.p + (off * pt.v.perpendicular()))
        return out

    def getAxisVector(self, dist, offset=0, endOffset=None):
        len = self.getAxisLength()
        o1 = offset
        o2 = endOffset if endOffset is not None else offset
        off = o1 + (o2-o1)*(dist/len)
        v = getArcVector(self.start.pt, self.end.pt, dist)
        return OPoint2d(Vec2d(v.p + (off * v.v.perpendicular())), v.v)

    def getAxisLength(self):
        return getArcLength(self.start.pt, self.end.pt)

    def createMesh(self):
        lstartoff = self.start.leftOffset()
        rstartoff = self.start.rightOffset()
        lendoff = self.end.leftOffset()
        rendoff = self.end.rightOffset()
        p0 = self.getOffsetAxis(0)
        plll = self.getOffsetAxis(lstartoff-self.innerBorder-self.outerBorder, lendoff-self.innerBorder-self.outerBorder)
        pll = self.getOffsetAxis(lstartoff-self.innerBorder, lendoff-self.innerBorder)
        pl = self.getOffsetAxis(lstartoff, lendoff)
        pr = self.getOffsetAxis(rstartoff, rendoff)
        prr = self.getOffsetAxis(rstartoff+self.innerBorder, rendoff+self.innerBorder)
        prrr = self.getOffsetAxis(rstartoff+self.innerBorder+self.outerBorder, rendoff+self.innerBorder+self.outerBorder)

        n = len(p0)
        pts = [None]*n*7

        # fill vertex buffer
        norm = Vec3d(0,0,1)
        for i in range(0, n):
            x = float(i)/3
            pts[ i       ] = Vertex(position=Vec3d(plll[i].x, plll[i].y, 0), normal=norm, texcoord=Tex2d(x,1), tangent=None, colour_diffuse=None)
            pts[ i +   n ] = Vertex(position=Vec3d(pll[i].x, pll[i].y, 0), normal=norm, texcoord=Tex2d(x,0.84), tangent=None, colour_diffuse=None)
            pts[ i + 2*n ] = Vertex(position=Vec3d(pl[i].x, pl[i].y, 0), normal=norm, texcoord=Tex2d(x,0.75), tangent=None, colour_diffuse=None)
            pts[ i + 3*n ] = Vertex(position=Vec3d(p0[i].x, p0[i].y, 0), normal=norm, texcoord=Tex2d(x,0), tangent=None, colour_diffuse=None)
            pts[ i + 4*n ] = Vertex(position=Vec3d(pr[i].x, pr[i].y, 0), normal=norm, texcoord=Tex2d(x,0.75), tangent=None, colour_diffuse=None)
            pts[ i + 5*n ] = Vertex(position=Vec3d(prr[i].x, prr[i].y, 0), normal=norm, texcoord=Tex2d(x,0.84), tangent=None, colour_diffuse=None)
            pts[ i + 6*n ] = Vertex(position=Vec3d(prrr[i].x,prrr[i].y, 0), normal=norm, texcoord=Tex2d(x,1), tangent=None, colour_diffuse=None)

        tris = []
        for i in range(0, 7-1):
            for j in range(0, n-1):
                a = j+i*n
                b = j+1+i*n
                c = j+(i+1)*n
                d = j+1+(i+1)*n
                tris.append((a, d, c))
                tris.append((a, b, d))

        return Mesh(pts, tris)
