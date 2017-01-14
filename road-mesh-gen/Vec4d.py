########################################################################
import operator
import math


class Vec4d(object):
    __slots__ = ['x', 'y', 'z', 'w']

    def __init__(self, x_or_quadruple, y=None, z=None, w=None):
        if y is None:
            self.x = x_or_quadruple[0]
            self.y = x_or_quadruple[1]
            self.z = x_or_quadruple[2]
            self.w = x_or_quadruple[3]
        else:
            self.x = x_or_quadruple
            self.y = y
            self.z = z
            self.w = w

    def __len__(self):
        return 4

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        elif key == 3:
            return self.w
        else:
            raise IndexError("Invalid subscript " + str(key) + " to Vec4d")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        elif key == 3:
            self.w = value
        else:
            raise IndexError("Invalid subscript " + str(key) + " to Vec4d")

    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec4d(%s, %s, %s, %s)' % (self.x, self.y, self.z, self.w)

    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 4:
            return self.x == other[0] and self.y == other[1] and self.z == other[2] and self.w == other[3]
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 4:
            return self.x != other[0] or self.y != other[1] or self.z != other[2] or self.w != other[3]
        else:
            return True

    def __nonzero__(self):
        return self.x or self.y or self.z or self.w

    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec3d"
        if isinstance(other, Vec4d):
            return Vec4d(f(self.x, other.x),
                         f(self.y, other.y),
                         f(self.z, other.z),
                         f(self.w, other.w))
        elif (hasattr(other, "__getitem__")):
            return Vec4d(f(self.x, other[0]),
                         f(self.y, other[1]),
                         f(self.z, other[2]),
                         f(self.w, other[3]))
        else:
            return Vec4d(f(self.x, other),
                         f(self.y, other),
                         f(self.z, other),
                         f(self.w, other))

    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec3d"
        if (hasattr(other, "__getitem__")):
            return Vec4d(f(other[0], self.x),
                         f(other[1], self.y),
                         f(other[2], self.z),
                         f(other[3], self.w))
        else:
            return Vec4d(f(other, self.x),
                         f(other, self.y),
                         f(other, self.z),
                         f(other, self.w))

    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
            self.z = f(self.z, other[2])
            self.w = f(self.w, other[3])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
            self.z = f(self.z, other)
            self.w = f(self.w, other)
        return self

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec4d):
            return Vec4d(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        elif hasattr(other, "__getitem__"):
            return Vec4d(self.x + other[0], self.y + other[1], self.z + other[2], self.w + other[3])
        else:
            return Vec4d(self.x + other, self.y + other, self.z + other, self.w + other)

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vec4d):
            self.x += other.x
            self.y += other.y
            self.z += other.z
            self.w += other.w
        elif hasattr(other, "__getitem__"):
            self.x += other[0]
            self.y += other[1]
            self.z += other[2]
            self.w += other[3]
        else:
            self.x += other
            self.y += other
            self.z += other
            self.w += other
        return self

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec4d):
            return Vec4d(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        elif (hasattr(other, "__getitem__")):
            return Vec4d(self.x - other[0], self.y - other[1], self.z - other[2], self.w - other[3])
        else:
            return Vec4d(self.x - other, self.y - other, self.z - other, self.w - other)
"""
    def __rsub__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(other.x - self.x, other.y - self.y, other.z - self.z)
        if (hasattr(other, "__getitem__")):
            return Vec3d(other[0] - self.x, other[1] - self.y, other[2] - self.z)
        else:
            return Vec3d(other - self.x, other - self.y, other - self.z)

    def __isub__(self, other):
        if isinstance(other, Vec3d):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        elif (hasattr(other, "__getitem__")):
            self.x -= other[0]
            self.y -= other[1]
            self.z -= other[2]
        else:
            self.x -= other
            self.y -= other
            self.z -= other
        return self

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec3d):
            return Vec3d(self.x * other.x, self.y * other.y, self.z * other.z)
        if (hasattr(other, "__getitem__")):
            return Vec3d(self.x * other[0], self.y * other[1], self.z * other[2])
        else:
            return Vec3d(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, Vec3d):
            self.x *= other.x
            self.y *= other.y
            self.z *= other.z
        elif (hasattr(other, "__getitem__")):
            self.x *= other[0]
            self.y *= other[1]
            self.z *= other[2]
        else:
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)

    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)

    def __idiv__(self, other):
        return self._io(other, operator.div)

    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)

    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)

    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)

    def __truediv__(self, other):
        return self._o2(other, operator.truediv)

    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)

    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)

    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)

    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)

    def __divmod__(self, other):
        return self._o2(other, operator.divmod)

    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)

    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)

    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)

    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)

    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)

    def __rshift__(self, other):
        return self._o2(other, operator.rshift)

    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)

    def __and__(self, other):
        return self._o2(other, operator.and_)

    __rand__ = __and__

    def __or__(self, other):
        return self._o2(other, operator.or_)

    __ror__ = __or__

    def __xor__(self, other):
        return self._o2(other, operator.xor)

    __rxor__ = __xor__

    # Unary operations
    def __neg__(self):
        return Vec3d(operator.neg(self.x), operator.neg(self.y), operator.neg(self.z))

    def __pos__(self):
        return Vec3d(operator.pos(self.x), operator.pos(self.y), operator.pos(self.z))

    def __abs__(self):
        return Vec3d(abs(self.x), abs(self.y), abs(self.z))

    def __invert__(self):
        return Vec3d(-self.x, -self.y, -self.z)

    # vectory functions
    def get_length_sqrd(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __setlength(self, value):
        length = self.get_length()
        self.x *= value / length
        self.y *= value / length
        self.z *= value / length

    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")


    def normalized(self):
        length = self.length
        if length != 0:
            return self / length
        return Vec3d(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return length

    def dot(self, other):
        return float(self.x * other[0] + self.y * other[1] + self.z * other[2])

    def get_distance(self, other):
        return math.sqrt((self.x - other[0]) ** 2 + (self.y - other[1]) ** 2 + (self.z - other[2]) ** 2)

    def get_dist_sqrd(self, other):
        return (self.x - other[0]) ** 2 + (self.y - other[1]) ** 2 + (self.z - other[2]) ** 2

    def projection(self, other):
        other_length_sqrd = other[0] * other[0] + other[1] * other[1] + other[2] * other[2]
        projected_length_times_other_length = self.dot(other)
        return other * (projected_length_times_other_length / other_length_sqrd)

    def cross(self, other):
        return Vec3d(self.y * other[2] - self.z * other[1], self.z * other[0] - self.x * other[2],
                     self.x * other[1] - self.y * other[0])

    def interpolate_to(self, other, range):
        return Vec3d(self.x + (other[0] - self.x) * range, self.y + (other[1] - self.y) * range,
                     self.z + (other[2] - self.z) * range)

    def convert_to_basis(self, x_vector, y_vector, z_vector):
        return Vec3d(self.dot(x_vector) / x_vector.get_length_sqrd(),
                     self.dot(y_vector) / y_vector.get_length_sqrd(),
                     self.dot(z_vector) / z_vector.get_length_sqrd())

    def __getstate__(self):
        return [self.x, self.y, self.z]

    def __setstate__(self, dict):
        self.x, self.y, self.z = dict

"""
