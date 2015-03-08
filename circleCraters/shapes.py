import math


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def is_collinear(cls, points, error=1E-6):
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
            determinant = (delta_a.x * delta_b.y) - (delta_a.y * delta_b.x)
            if abs(determinant) > error:
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

    @property
    def length(self):
        return math.sqrt(sum([delta ** 2 for delta in self.delta]))

    @property
    def midpoint(self):
        return (self.points[0] + self.points[1]) * 0.5

    @property
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

        if Point.is_collinear(vertices):
            raise ValueError('vertices are collinear')

        self.vertices = vertices

    @property
    def center(self):
        a = Line(self.vertices[0], self.vertices[1]).perpendicular_bisector()
        b = Line(self.vertices[1], self.vertices[2]).perpendicular_bisector()
        return a.intersection(b)

    @property
    def radius(self):
        return Line(self.center, self.vertices[0]).length

    def __repr__(self):
        return 'Circle(%s, %s, %s)' % self.vertices


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
