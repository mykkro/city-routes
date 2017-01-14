from meshxml import Mesh


class MeshBuilder(object):
    def __init__(self):
        self.vertexMap = {}
        self.vertexIndexMap = {}
        self.vertexNames = []
        self.triangles = []

    def addVertex(self, name, vertex):
        if name not in self.vertexMap:
            self.vertexMap[name] = vertex;
            self.vertexIndexMap[name] = len(self.vertexNames)
            self.vertexNames.append(name)
        else:
            self.vertexMap[name] = vertex;

    def addTriangle(self, nameA, nameB, nameC):
        self.triangles.append((nameA, nameB, nameC))

    def getVertex(self, name):
        return self.vertexMap[name]

    def stitchVertices(self, anames, bnames):
        # stitch the vertices together
        a = 0
        b = 0
        amax = len(anames)-1
        bmax = len(bnames)-1
        while a < amax or b < bmax:
            # there are remaining vertices
            va = anames[a]
            vb = bnames[b]
            if a == amax:
                # the next vertex is in 'b' row
                vc = bnames[b+1]
                b += 1
            elif b == bmax:
                vc = anames[a+1]
                a += 1
            else:
                vca = anames[a+1]
                vcb = bnames[b+1]
                # which side is shorter?
                if self.getVertex(va).position.get_distance(self.getVertex(vcb).position) < self.getVertex(vb).position.get_distance(self.getVertex(vca).position):
                    # choose vcb
                    vc = vcb
                    b += 1
                else:
                    vc = vca
                    a += 1
            # draw the triangle
            self.addTriangle(va, vc, vb)


    def getMesh(self):
        vertices = [None] * len(self.vertexNames)
        for key in self.vertexMap:
            index = self.vertexIndexMap[key]
            vertices[index] = self.vertexMap[key]
        triangles = []
        for tri in self.triangles:
            triangles.append((self.vertexIndexMap[tri[0]], self.vertexIndexMap[tri[1]], self.vertexIndexMap[tri[2]]))
        return Mesh(vertices, triangles)

