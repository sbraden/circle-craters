import numpy as np
import requests
from qgis.core import QgsPointXY
import math


class cached_property(object):  # noqa
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return self

        try:
            return obj.__dict__[self.__name__]
        except KeyError:
            pass

        value = self.func(obj)
        obj.__dict__[self.__name__] = value
        return value


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def is_collinear(cls, points, error=1E-9):
        points = list(set(points))
        if len(points) == 0:
            return False

        if len(points) <= 2:
            return True  # two points always form a line

        p1 = points.pop()
        p2 = points.pop()
        delta_a = p2 - p1

        for point in points:
            delta_b = point - p1
            # cosine of delta_a and delta_b
            determinant = (delta_a.x * delta_b.x + delta_a.y * delta_b.y)/math.sqrt(delta_a.x**2+delta_a.y**2)/math.sqrt(delta_b.x**2+delta_b.y**2)
            if (1.0 - abs(determinant)) > error:
                return False

        return True

    def __neg__(self):
        return self * -1

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Point(other * self.x, other * self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self):
        return 'Point(%s, %s)' % (self.x, self.y)


class Line(object):
    def __init__(self, *points):
        if len(points) != 2:
            raise ValueError('a line must have two points')
        self.points = points

    @cached_property
    def length(self):
        return math.sqrt(sum([delta ** 2 for delta in self.delta]))

    @cached_property
    def midpoint(self):
        return (self.points[0] + self.points[1]) * 0.5

    @cached_property
    def delta(self):
        return self.points[0] - self.points[1]

    def perpendicular_line(self, point):
        endpoint = Point(point.x - self.delta.y, point.y + self.delta.x)
        return Line(point, endpoint)

    def perpendicular_bisector(self):
        return self.perpendicular_line(self.midpoint)

    def intersection(self, other):
        # http://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        x3, y3 = other.points[0]
        x4, y4 = other.points[1]

        det_a = (x1 * y2) - (y1 * x2)
        det_b = (x3 * y4) - (y3 * x4)

        denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
        x = (det_a * (x3 - x4)) - ((x1 - x2) * det_b)
        y = (det_a * (y3 - y4)) - ((y1 - y2) * det_b)

        return Point(x / denominator, y / denominator)

    def __repr__(self):
        return 'Line(%s, %s)' % self.points


class Circle(object):
    def __init__(self, *vertices):
        if len(vertices) != 3:
            raise ValueError('a circle must have three vertices')

        if Point.is_collinear(vertices, error=1e-2):
            raise ValueError('vertices are collinear')

        self.vertices = vertices

    @cached_property
    def center(self):
        a = Line(self.vertices[0], self.vertices[1]).perpendicular_bisector()
        b = Line(self.vertices[1], self.vertices[2]).perpendicular_bisector()
        return a.intersection(b)

    @cached_property
    def radius(self):
        return Line(self.center, self.vertices[0]).length

    @cached_property
    def diameter(self):
        return 2 * self.radius

    def point_at(self, theta):
        return Point(
            self.radius * math.cos(theta) + self.center.x,
            self.radius * math.sin(theta) + self.center.y
        )

    def to_polygon(self, segments=64):
        thetas = [(2 * math.pi) / segments * i for i in range(segments)]
        return [self.point_at(theta) for theta in thetas]

    def __repr__(self):
        return 'Circle(%s, %s, %s)' % self.vertices

def sample_area_around(rlayer, x, y, r=16):
    xvalues = np.arange(x-r, x+r)
    yvalues = np.arange(y-r, y+r)
    output = []
    for y in yvalues[::-1]:
        for x in xvalues:
            val, res = rlayer.dataProvider().sample(QgsPointXY(x, y), 1)
            output.append(val)
    return output

def make_request(pixels):
    url = "http://localhost:8501/detect/"
    body = {"instances": [pixels]}
    r = requests.post(url=url, json=body)
    return r.json()

def do_detection(rlayer, x, y, r=16):
    pixels = sample_area_around(rlayer, x, y, r=r)
    response = make_request(pixels)
    x, y, r = response['predictions']
    return x, y, r

class DetectedCircle(object):
    def __init__(self, rlayer, x_in, y_in, r_in=16):
        x, y, r = do_detection(rlayer, x_in, y_in, r=r_in)
        self.a = x_in + (x - r_in)
        self.b = y_in + (r_in - y)
        self.r = r

    @cached_property
    def center(self):
        #a = Line(self.vertices[0], self.vertices[1]).perpendicular_bisector()
        #b = Line(self.vertices[1], self.vertices[2]).perpendicular_bisector()
        return (self.a, self.b)

    @cached_property
    def radius(self):
        #return Line(self.center, self.vertices[0]).length
        return self.r

    @cached_property
    def diameter(self):
        return 2 * self.radius

    def point_at(self, theta):
        return Point(
            self.radius * math.cos(theta) + self.a,
            self.radius * math.sin(theta) + self.b
        )

    def to_polygon(self, segments=64):
        thetas = [(2 * math.pi) / segments * i for i in range(segments)]
        return [self.point_at(theta) for theta in thetas]

    def __repr__(self):
        return 'Circle({}, {}, {})'.format(self.a, self.b, self.r)

if __name__ == '__main__':
    circle = Circle(Point(1, 0), Point(0, 1), Point(-1, 0))
    assert circle.center == Point(0, 0)
    assert circle.radius == 1

    circle = Circle(Point(1, -1), Point(0, 0), Point(-1, -1))
    assert circle.center == Point(0, -1)
    assert circle.radius == 1

    circle = Circle(Point(2.5, -2.5), Point(0, 0), Point(-2.5, -2.5))
    assert circle.center == Point(0, -2.5)
    assert circle.radius == 2.5

    # Test horizonatal line
    circle = Circle(Point(1, 0), Point(-1, 0), Point(0, 1))
    assert circle.center == Point(0, 0)
    assert circle.radius == 1

    # Test vertical line
    circle = Circle(Point(0, -1), Point(0, 1), Point(1, 0))
    assert circle.center == Point(0, 0)
    assert circle.radius == 1

    # Test collinear
    try:
        Circle(Point(0, -1), Point(0, 0), Point(0, 1))
        raise Exception('expect ValueError for collinear points')
    except ValueError:
        pass

    try:
        Circle(Point(0, -1), Point(0, 1), Point(0, 0))
        raise Exception('expect ValueError for collinear points')
    except ValueError:
        pass

    try:
        Circle(Point(0, 0), Point(0, 0), Point(0, 1))
        raise Exception('expect ValueError for collinear points')
    except ValueError:
        pass

    try:
        Circle(Point(0, 0), Point(0, 0), Point(0, 0))
        raise Exception('expect ValueError for collinear points')
    except ValueError:
        pass
