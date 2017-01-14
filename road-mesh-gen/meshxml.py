import xml.etree.cElementTree as ET
import os
from shutil import copy

from Vec3d import Vec3d
from Vec4d import Vec4d
from Tex2d import Tex2d


def meshXML(vertices, submeshes, useTangents=False):
    mesh = ET.Element("mesh")

    sharedgeometry = sharedGeometryXML(mesh, vertexcount=len(vertices))
    vertexbuffer = vertexBufferXML(sharedgeometry, tangents=useTangents)
    for vertex in vertices:
        vertexXML(vertexbuffer, vertex)

    for sm in submeshes:
        submeshesNode = submeshesXML(mesh)
        submesh = submeshXML(submeshesNode,  material=sm.material)
        facesNode = facesXML(submesh, count=len(sm.faces))
        for face in sm.faces:
            faceXML(facesNode, face[0], face[1], face[2])

    return mesh


def submeshesXML(mesh):
    submeshes = ET.SubElement(mesh, "submeshes")
    return submeshes


def submeshXML(submeshes, material=None, usesharedvertices="true", use32bitindexes="false", operationtype="triangle_list"):
    submesh = ET.SubElement(submeshes, "submesh")
    submesh.set("material", material)
    submesh.set("usesharedvertices", usesharedvertices)
    submesh.set("use32bitindexes", use32bitindexes)
    submesh.set("operationtype", operationtype)
    return submesh


def facesXML(submesh, count=0):
    faces = ET.SubElement(submesh, "faces")
    faces.set("count", "%d" % count)
    return faces


def faceXML(faces, v1=0, v2=1, v3=2):
    face = ET.SubElement(faces, "face")
    face.set("v1", "%d" % v1)
    face.set("v2", "%d" % v2)
    face.set("v3", "%d" % v3)
    return face


def sharedGeometryXML(mesh, vertexcount=0):
    sharedgeometry = ET.SubElement(mesh, "sharedgeometry")
    sharedgeometry.set("vertexcount", "%d" % vertexcount)
    return sharedgeometry


def vertexBufferXML(sharedgeometry, positions=True, normals=True, texture_coord_dimensions_0="float2", tangents=True, colours_diffuse=False, tangent_dimensions=4, texture_coords=1 ):
    vertexbuffer = ET.SubElement(sharedgeometry, "vertexbuffer")
    vertexbuffer.set("positions", "true" if positions else "false")
    vertexbuffer.set("normals", "true" if normals else "false")
    vertexbuffer.set("colours_diffuse", "true" if colours_diffuse else "false")
    vertexbuffer.set("tangents", "true" if tangents else "false")
    vertexbuffer.set("tangent_dimensions", "%d" % tangent_dimensions)
    vertexbuffer.set("texture_coord_dimensions_0", texture_coord_dimensions_0)
    vertexbuffer.set("texture_coords", "%d" % texture_coords)
    return vertexbuffer


def position3dXML(vertex, vec3d):
    position = ET.SubElement(vertex, "position")
    position.set("x", "%f" % vec3d.x)
    position.set("y", "%f" % vec3d.y)
    position.set("z", "%f" % vec3d.z)
    return position


def normal3dXML(vertex, vec3d):
    normal = ET.SubElement(vertex, "normal")
    normal.set("x", "%f" % vec3d.x)
    normal.set("y", "%f" % vec3d.y)
    normal.set("z", "%f" % vec3d.z)
    return normal


def texcoord2dXML(vertex, tex2d):
    texcoord = ET.SubElement(vertex, "texcoord")
    texcoord.set("u", "%f" % tex2d.u)
    texcoord.set("v", "%f" % tex2d.v)
    return texcoord


def tangent4dXML(vertex, vec4d):
    tangent = ET.SubElement(vertex, "tangent")
    tangent.set("x", "%f" % vec4d.x)
    tangent.set("y", "%f" % vec4d.y)
    tangent.set("z", "%f" % vec4d.z)
    tangent.set("w", "%f" % vec4d.w)
    return tangent


def colourDiffuseXML(vertex, rgba):
    colour_diffuse = ET.SubElement(vertex, "colour_diffuse")
    colour_diffuse.set("value", "%f %f %f %f" % (rgba[0], rgba[1], rgba[2], rgba[3]))
    return colour_diffuse


def vertexXML(vertexbuffer, v):
    vertex = ET.SubElement(vertexbuffer, "vertex")
    position3dXML(vertex, v.position)
    if v.normal is not None:
        normal3dXML(vertex, v.normal)
    if v.texcoord is not None:
        texcoord2dXML(vertex, v.texcoord)
    if v.tangent is not None:
        tangent4dXML(vertex, v.tangent)
    if v.colour_diffuse is not None:
        colourDiffuseXML(vertex, v.colour_diffuse)
    return vertex




class Submesh(object):
    __slots__ = ['material', 'faces']

    def __init__(self, material, faces):
        self.material = material
        self.faces = faces


class Mesh(object):
    __slots__ = ['vertices', 'faces']

    def __init__(self, v=[], t=[]):
        self.vertices = v
        self.faces = t


    def addMesh(self, m):
        inv = len(self.vertices)
        inf = len(self.faces)
        self.vertices = self.vertices + m.vertices
        self.faces = self.faces + m.faces
        for i in range(inf, len(self.faces)):
            face = self.faces[i]
            newf = [0] * len(face)
            for j in range(0, len(face)):
                newf[j] = face[j] + inv
            self.faces[i] = tuple(newf)




def generateGcolTrimesh(mesh, material):
    out = []
    out.append("""TCOL1.0

attributes {
    static;
}

compound {
}
trimesh {
    vertexes {""")
    for v in mesh.vertices:
        out.append("        %f %f %f;" % (v.position.x, v.position.y, v.position.z));
    out.append("""    }
    faces {""")
    for f in mesh.faces:
        out.append("        %d %d %d \"%s\";" % (f[0], f[1], f[2], material))
    out.append("""    }
}
""")
    return "\n".join(out)


def exportMesh(mesh, name, material, cmaterial):
    mxml = meshXML(mesh.vertices, [Submesh(material, mesh.faces)])

    tree = ET.ElementTree(mxml)
    tree.write("%s.xml" % name)


    trimesh = generateGcolTrimesh(mesh, cmaterial)
    with open('%s.gcol' % name, 'w') as f:
        f.write(trimesh)

    # convert mesh
    dir = os.getcwd()
    os.chdir("bin")
    os.system('OgreXMLConverter.exe ../%s.xml ../%s.mesh' % (name, name))
    os.chdir(dir)

    # copy mesh and gcol to target directory
    TARGETDIR = "C:/Work/grit/playground/img"
    copy("%s.mesh" % name, "%s/%s.mesh" % (TARGETDIR, name))
    copy("%s.gcol" % name, "%s/%s.gcol" % (TARGETDIR, name))
