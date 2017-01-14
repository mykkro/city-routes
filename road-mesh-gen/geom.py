import math
from math import sqrt
from Vec2d import Vec2d

def checkLineIntersection(line1StartX, line1StartY, line1EndX, line1EndY, line2StartX, line2StartY, line2EndX, line2EndY):
    # if the lines intersect, the result contains the x and y of the intersection (treating the lines as infinite) and booleans for whether line segment 1 or line segment 2 contain the point
    result = {
        "x": None,
        "y": None,
        "onLine1": False,
        "onLine2": False
    }
    denominator = ((line2EndY - line2StartY) * (line1EndX - line1StartX)) - ((line2EndX - line2StartX) * (line1EndY - line1StartY))
    if denominator == 0:
        return result;

    a = line1StartY - line2StartY;
    b = line1StartX - line2StartX;
    numerator1 = ((line2EndX - line2StartX) * a) - ((line2EndY - line2StartY) * b);
    numerator2 = ((line1EndX - line1StartX) * a) - ((line1EndY - line1StartY) * b);
    a = numerator1 / denominator;
    b = numerator2 / denominator;

    # if we cast these lines infinitely in both directions, they intersect here:
    result["x"] = line1StartX + (a * (line1EndX - line1StartX));
    result["y"] = line1StartY + (a * (line1EndY - line1StartY));

    # if line1 is a segment and line2 is infinite, they intersect if:
    if a > 0 and a < 1:
        result["onLine1"] = True

    # if line2 is a segment and line1 is infinite, they intersect if:
    if b > 0 and b < 1:
        result["onLine2"] = True

    # if line1 and line2 are segments, they intersect if both of the above are true
    return result;


def circleHalfLineIntersection(cx, cy, r, x0, y0, u, v):
	# Finding intersection between circle (cx, cy, r) and halfline (x0, y0, u, v)
    # solve quadratic equation ax^2 + bx + c = 0
	# circle: |X-C|^2 = (X-C)(X-C) = r^2
	# point: X = P + tU
	# -> (P + tU - C)(P + tU - C) = r^2
	# -> (tU + (P-C))(tU + (P-C)) - r^2 = 0
	# -> (tU)^2 + (P-C)^2 + 2*tU*(P-C) - r^2 = 0
	# -> t^2*(U^2) + t*(2*U*(P-C)) + (P-C)^2 - r^2 = 0
	# Quadratic equation:
	# a = U^2 = (u,v)*(u,v) = u*u + v*v;
	# b = 2*U*(P-C) = 2*(u,v)*(x0-cx,y0-cy) = 2*(u*(x0-cx)+v*(y0-cy)) = 2*u*x0 - 2*u*cx + 2*v*y0 - 2*v*cy
	# c = (P-C)^2 - r^2 = P^2 + C^2 - 2PC - r^2 = x0*x0 + y0*y0 + cx*cx + cy*cy - 2*(x0*cx+y0*cy) - r^2
	uv = Vec2d(u,v).normalized()
	u = uv.x;
	v = uv.y;
	a = u*u + v*v; # U^2
	b = 2*(u*x0 - u*cx + v*y0 - v*cy)
	c = x0*x0 + y0*y0 + cx*cx + cy*cy - 2*(x0*cx+y0*cy) - r*r
	D = b*b - 4*a*c
	if(D>=0):
		# two solutions
		d = math.sqrt(D);
		t1 = (-b+d)/(2*a); # take only this t - it is positive
		return Vec2d(x0 + t1*u, y0 + t1*v)
	else:
		# "No real solution!"
		return None


# Determines whether two circles collide and, if applicable,
# the points at which their borders intersect.
# Based on an algorithm described by Paul Bourke:
# http://local.wasp.uwa.edu.au/~pbourke/geometry/2circle/
# Arguments:
#   P0 (Vec2d): the centre point of the first circle
#   P1 (vec2d): the centre point of the second circle
#   r0 (numeric): radius of the first circle
#   r1 (numeric): radius of the second circle
# Returns:
#   False if the circles do not collide
#   True if one circle wholly contains another such that the borders
#       do not overlap, or overlap exactly (e.g. two identical circles)
#   An array of two Vec2d points containing the intersection points
#       if the circle's borders intersect.
def circleIntersection(P0, P1, r0, r1):
    # d = distance
    d = sqrt((P1.x - P0.x)**2 + (P1.y - P0.y)**2)
    # n**2 in Python means "n to the power of 2"
    # note: d = a + b

    if d > (r0 + r1):
        return False
    elif d < abs(r0 - r1):
        return True
    elif d == 0:
        return True
    else:
        a = (r0**2 - r1**2 + d**2) / (2 * d)
        b = d - a
        h = sqrt(r0**2 - a**2)
        P2 = P0 + a * (P1 - P0) / d

        i1x = P2.x + h * (P1.y - P0.y) / d
        i1y = P2.y - h * (P1.x - P0.x) / d
        i2x = P2.x - h * (P1.y - P0.y) / d
        i2y = P2.y + h * (P1.x - P0.x) / d

        i1 = Vec2d(i1x, i1y)
        i2 = Vec2d(i2x, i2y)

        return [i1, i2]