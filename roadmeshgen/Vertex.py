class Vertex(object):
    __slots__ = ['position', 'normal', 'texcoord', 'tangent', 'colour_diffuse']

    def __init__(self, position, normal=None, texcoord=None, tangent=None, colour_diffuse=None):
        self.position = position
        self.normal = normal
        self.texcoord = texcoord
        self.tangent = tangent
        self.colour_diffuse = colour_diffuse
