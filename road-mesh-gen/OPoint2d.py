import math

class OPoint2d(object):
    """2d point with an orientation vector.
       """
    __slots__ = ['p', 'v']

    def __init__(self, p, v):
        self.p = p
        self.v = v.normalized()

    def __repr__(self):
        return 'OPoint2d.py(%s, %s, %s, %s)' % (self.p.x, self.p.y, self.v.x, self.v.y)
