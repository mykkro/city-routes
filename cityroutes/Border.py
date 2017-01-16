from roadmeshgen.Vec2d import Vec2d


class Border(object):
    __slots__ = ['points']

    # points = array of Vec2d, sorted by increasing x, min length: 2, x0=0
    # sequence of x is rising monotonously
    def __init__(self, points):
        self.points = points

    def length(self):
        return self.points[-1].x

    def flipped(self):
        return Border(map(lambda pt: Vec2d(pt.x, -pt.y), self.points))

    # get width of the border in a given point
    # 0 <= d <= self.length()
    def width(self, d):
        if d<0:
            return self.points[0].y
        index = 0
        while index < len(self.points)-1:
            pt1 = self.points[index]
            pt2 = self.points[index+1]
            if (d >= pt1.x) and (d < pt2.x):
                alpha = float(d - pt1.x)/(pt2.x-pt1.x)
                width = pt1.y*(1-alpha) + pt2.y*alpha
                return width
            index += 1
        return self.points[-1].y

    # join the borders together (horizontally), one after another. The y coordinates of overlap points should match
    @staticmethod
    def merge(borders):
        lengths = map(lambda b: b.length(), borders)
        x = 0
        points = []
        pt = borders[0].points[0]
        points.append(Vec2d(x+pt.x, pt.y))
        for i in range(0, len(borders)):
            bb = borders[i]
            ll = lengths[i]
            for pt in bb.points[1:]:
                points.append(Vec2d(x+pt.x, pt.y))
            x += ll
        return Border(points)

    # returns this border joined with another border (vertically)
    # the lengths of the borders should be equal
    def join(self, b, add=True):
        b1 = self
        b2 = b
        x = []
        points1 = []
        points2 = []
        i1 = 0
        i2 = 0
        while i1 < len(b1.points) and i2 < len(b2.points):
            p1 = b1.points[i1]
            p2 = b2.points[i2]
            if p1.x == p2.x:
                x.append(p1.x)
                points1.append(p1.y)
                points2.append(p2.y)
                i1 += 1
                i2 += 1
            elif p1.x < p2.x:
                x.append(p1.x)
                points1.append(p1.y)
                points2.append(b2.width(p1.x))
                i1 += 1
            else:
                x.append(p2.x)
                points2.append(p2.y)
                points1.append(b1.width(p2.x))
                i2 += 1
        points = [0] * len(x)
        for i in range(0, len(x)):
            if add:
                result = points1[i] + points2[i]
            else:
                result = points1[i] - points2[i]
            points[i] = Vec2d(x[i], result)
        return Border(points)
