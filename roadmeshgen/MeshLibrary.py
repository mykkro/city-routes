from meshutils import exportMesh


class MeshLibrary(object):
    def __init__(self):
        self.meshes = {}

    def addMesh(self, mesh, className, material="DEFAULT", collisionMaterial="/common/pmat/Stone", parentClass="BaseClass", classAttrs={}):
        self.meshes[className] = {
            "mesh": mesh,
            "className": className,
            "material": material,
            "collisionMaterial": collisionMaterial,
            "classAttrs": classAttrs,
            "parentClass": parentClass
        }

    def exportMeshes(self):
        for key in self.meshes:
            m = self.meshes[key]
            exportMesh(m["mesh"], m["className"], m["material"], m["collisionMaterial"])

    def exportClasses(self, ls):
        for key in self.meshes:
            m = self.meshes[key]
            ls.addClass(m["className"], m["parentClass"], m["classAttrs"])
