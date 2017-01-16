import svgwrite
import random


class CityRoutesSVGGenerator:
    def __init__(self):
        self.dwg = svgwrite.Drawing('test.svg', profile='tiny', size=(1000, 1000))

    def test(self):
        self.dwg.add(self.dwg.line((0, 0), (1000, 1000), stroke=svgwrite.rgb(10, 10, 16, '%')))
        self.dwg.add(self.dwg.text('Test', insert=(200, 100), fill='red'))

    def save(self):
        self.dwg.save()

    def color(self, r, g, b):
        return svgwrite.rgb(r, g, b, '%')

    def randomcolor(self, rmin=0, gmin=0, bmin=0, rmax=100, gmax=100, bmax=100):
        r = random.random()*(rmax-rmin) + rmin
        g = random.random()*(gmax-gmin) + gmin
        b = random.random()*(bmax-bmin) + bmin
        return self.color(r,g,b)

    def grid(self):
        col = svgwrite.rgb(80, 80, 80, '%')
        for i in range(0, 100):
            self.dwg.add(self.dwg.line((i*10, 0), (i*10, 1000), stroke=col))
            self.dwg.add(self.dwg.line((0, i*10), (1000, i*10), stroke=col))

    def bigpoint(self, vec, radius=5):
        self.dwg.add(self.dwg.circle((vec.x, vec.y), radius, fill=svgwrite.rgb(0,0,0, '%')))

    def arrowpoint(self, pos, dir, radius=5, length=20):
        dir = dir.normalized()
        color = svgwrite.rgb(0,0,0, '%')
        self.dwg.add(self.dwg.circle((pos.x, pos.y), radius, fill=color))
        self.dwg.add(self.dwg.line((pos.x, pos.y), (pos.x+length*dir.x, pos.y+length*dir.y), stroke=color))

    def line(self, start, end, color):
        self.dwg.add(self.dwg.line((start.x, start.y), (end.x, end.y), stroke=color, stroke_width=3))

    def rect(self, pos, size, color):
        self.dwg.add(self.dwg.rect((pos.x, pos.y), (size.x, size.y), fill=color))

    def path(self, points, color):
        d = " ".join(map(lambda (i,p): "%s%.1f,%.1f" % ("M" if i==0 else "L", p.x, p.y), enumerate(points))) + "z"
        self.dwg.add(self.dwg.path(d=d, fill=color))

    def edge(self, edge):
        start = edge.start.position.vec2d()
        end = edge.end.position.vec2d()
        self.node(edge.start)
        self.node(edge.end)
        self.line(start, end, self.color(80, 80, 70))

    def node(self, node):
        self.bigpoint(node.position.vec2d())
