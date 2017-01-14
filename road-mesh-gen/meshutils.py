from Vec3d import Vec3d
from Tex2d import Tex2d
from Vertex import Vertex
from meshxml import meshXML, Submesh, Mesh, generateGcolTrimesh, exportMesh


# creates a XY plane [-size..size]*[-size..size] centered at [0,0,0]
def makePlaneMesh(size, tx1=-1, tx2=1, ty1=1, ty2=-1):
    z = 0
    nz = Vec3d(0,0,1)
    tngt = None

    return Mesh([
        # vertices
        Vertex(position=Vec3d(-size, -size, z), normal=nz, texcoord=Tex2d(tx1, ty1), tangent=tngt),
        Vertex(position=Vec3d(0, -size, z), normal=nz, texcoord=Tex2d(0, ty1), tangent=tngt),
        Vertex(position=Vec3d(0, 0, z), normal=nz, texcoord=Tex2d(0, 0), tangent=tngt),
        Vertex(position=Vec3d(-size, 0, z), normal=nz, texcoord=Tex2d(tx1, 0), tangent=tngt),
        Vertex(position=Vec3d(size, -size, z), normal=nz, texcoord=Tex2d(tx2, ty1), tangent=tngt),
        Vertex(position=Vec3d(size, 0, z), normal=nz, texcoord=Tex2d(tx2, 0), tangent=tngt),
        Vertex(position=Vec3d(0, size, z), normal=nz, texcoord=Tex2d(0, ty2), tangent=tngt),
        Vertex(position=Vec3d(-size, size, z), normal=nz, texcoord=Tex2d(tx1, ty2), tangent=tngt),
        Vertex(position=Vec3d(size, size, z), normal=nz, texcoord=Tex2d(tx2, ty2), tangent=tngt)
    ], [
        # faces
        [0, 1, 2],
        [2, 3, 0],
        [1, 4, 5],
        [5, 2, 1],
        [3, 2, 6],
        [6, 7, 3],
        [2, 5, 8],
        [8, 6, 2]
    ])


# creates a cube [-size..size]*[-size..size] centered at [0,0,0]
def makeCubeMesh(size=1):
    vertices = [
       Vertex(position=Vec3d(0.5,-0.5,1.0)*size, normal=Vec3d(0.408248,-0.816497,0.408248), texcoord=Tex2d(1,0)),
       Vertex(position=Vec3d(-0.5,-0.5,0.0)*size, normal=Vec3d(-0.408248,-0.816497,-0.408248), texcoord=Tex2d(0,1)),
       Vertex(position=Vec3d(0.5,-0.5,0.0)*size, normal=Vec3d(0.666667,-0.333333,-0.666667), texcoord=Tex2d(1,1)),
       Vertex(position=Vec3d(-0.5,-0.5,1.0)*size, normal=Vec3d(-0.666667,-0.333333,0.666667), texcoord=Tex2d(0,0)),
       Vertex(position=Vec3d(0.5,0.5,1.0)*size, normal=Vec3d(0.666667,0.333333,0.666667), texcoord=Tex2d(1,0)),
       Vertex(position=Vec3d(-0.5,-0.5,1.0)*size, normal=Vec3d(-0.666667,-0.333333,0.666667), texcoord=Tex2d(0,1)),
       Vertex(position=Vec3d(0.5,-0.5,1.0)*size, normal=Vec3d(0.408248,-0.816497,0.408248), texcoord=Tex2d(1,1)),
       Vertex(position=Vec3d(-0.5,0.5,1.0)*size, normal=Vec3d(-0.408248,0.816497,0.408248), texcoord=Tex2d(0,0)),
       Vertex(position=Vec3d(-0.5,0.5,0.0)*size, normal=Vec3d(-0.666667,0.333333,-0.666667), texcoord=Tex2d(0,1)),
       Vertex(position=Vec3d(-0.5,-0.5,0.0)*size, normal=Vec3d(-0.408248,-0.816497,-0.408248), texcoord=Tex2d(1,1)),
       Vertex(position=Vec3d(-0.5,-0.5,1.0)*size, normal=Vec3d(-0.666667,-0.333333,0.666667), texcoord=Tex2d(1,0)),
       Vertex(position=Vec3d(0.5,-0.5,0.0)*size, normal=Vec3d(0.666667,-0.333333,-0.666667), texcoord=Tex2d(0,1)),
       Vertex(position=Vec3d(0.5,0.5,0.0)*size, normal=Vec3d(0.408248,0.816497,-0.408248), texcoord=Tex2d(1,1)),
       Vertex(position=Vec3d(0.5,-0.5,1.0)*size, normal=Vec3d(0.408248,-0.816497,0.408248), texcoord=Tex2d(0,0)),
       Vertex(position=Vec3d(0.5,-0.5,0.0)*size, normal=Vec3d(0.666667,-0.333333,-0.666667), texcoord=Tex2d(1,0)),
       Vertex(position=Vec3d(-0.5,-0.5,0.0)*size, normal=Vec3d(-0.408248,-0.816497,-0.408248), texcoord=Tex2d(0,0)),
       Vertex(position=Vec3d(-0.5,0.5,1.0)*size, normal=Vec3d(-0.408248,0.816497,0.408248), texcoord=Tex2d(1,0)),
       Vertex(position=Vec3d(0.5,0.5,0.0)*size, normal=Vec3d(0.408248,0.816497,-0.408248), texcoord=Tex2d(0,1)),
       Vertex(position=Vec3d(-0.5,0.5,0.0)*size, normal=Vec3d(-0.666667,0.333333,-0.666667), texcoord=Tex2d(1,1)),
       Vertex(position=Vec3d(0.5,0.5,1.0)*size, normal=Vec3d(0.666667,0.333333,0.666667), texcoord=Tex2d(0,0))
    ]
    faces = [
        [0,1,2],      [3,1,0],
        [4,5,6],      [4,7,5],
        [8,9,10],      [10,7,8],
        [4,11,12],   [4,13,11],
        [14,8,12],   [14,15,8],
        [16,17,18],   [16,19,17]
    ]
    return Mesh(vertices, faces)


def makeTrueBoxMesh(x1=-0.5, x2=0.5, y1=-0.5, y2=0.5, z1=0, z2=1):
    a00 = Vec3d(x1, y1, z1)
    a01 = Vec3d(x2, y1, z1)
    a10 = Vec3d(x1, y2, z1)
    a11 = Vec3d(x2, y2, z1)
    b00 = Vec3d(x1, y1, z2)
    b01 = Vec3d(x2, y1, z2)
    b10 = Vec3d(x1, y2, z2)
    b11 = Vec3d(x2, y2, z2)
    nfront = Vec3d(0,-1,0)
    nback = Vec3d(0,-1,0)
    nleft = Vec3d(-1,0,0)
    nright = Vec3d(1,0,0)
    nup = Vec3d(0,0,1)
    ndown = Vec3d(0,0,-1)
    vertices = [
        # front
        Vertex(position=a00, normal=nfront, texcoord=Tex2d(0,0)),
        Vertex(position=b00, normal=nfront, texcoord=Tex2d(0,1)),
        Vertex(position=b01, normal=nfront, texcoord=Tex2d(1,1)),
        Vertex(position=a01, normal=nfront, texcoord=Tex2d(1,0)),
        # back
        Vertex(position=b10, normal=nback, texcoord=Tex2d(0,1)),
        Vertex(position=a10, normal=nback, texcoord=Tex2d(0,0)),
        Vertex(position=a11, normal=nback, texcoord=Tex2d(1,0)),
        Vertex(position=b11, normal=nback, texcoord=Tex2d(1,1)),
        # left
        Vertex(position=a10, normal=nleft, texcoord=Tex2d(0,0)),
        Vertex(position=b10, normal=nleft, texcoord=Tex2d(0,1)),
        Vertex(position=b00, normal=nleft, texcoord=Tex2d(1,1)),
        Vertex(position=a00, normal=nleft, texcoord=Tex2d(1,0)),
        # right
        Vertex(position=a01, normal=nright, texcoord=Tex2d(0,0)),
        Vertex(position=b01, normal=nright, texcoord=Tex2d(0,1)),
        Vertex(position=b11, normal=nright, texcoord=Tex2d(1,1)),
        Vertex(position=a11, normal=nright, texcoord=Tex2d(1,0)),
        # top
        Vertex(position=b00, normal=nup, texcoord=Tex2d(0,0)),
        Vertex(position=b10, normal=nup, texcoord=Tex2d(0,1)),
        Vertex(position=b11, normal=nup, texcoord=Tex2d(1,1)),
        Vertex(position=b01, normal=nup, texcoord=Tex2d(1,0)),
        # bottom
        Vertex(position=a10, normal=ndown, texcoord=Tex2d(0,0)),
        Vertex(position=a00, normal=ndown, texcoord=Tex2d(0,1)),
        Vertex(position=a01, normal=ndown, texcoord=Tex2d(1,1)),
        Vertex(position=a11, normal=ndown, texcoord=Tex2d(1,0)),
    ]
    faces = [
        [0,3,2],      [2,1,0],
        [4,7,6],      [6,5,4],
        [8,11,10],    [10,9,8],
        [12,15,14],   [14,13,12],
        [16,19,18],   [18,17,16],
        [20,23,22],   [22,21,20]
    ]
    return Mesh(vertices, faces)


def makeTrueCubeMesh(size=1):
    hs = size/2
    x1 = -hs*size
    x2 = hs*size
    y1 = -hs*size
    y2 = hs*size
    z1 = 0
    z2 = 2*hs*size
    return makeTrueBoxMesh(x1, x2, y1, y2, z1, z2)


