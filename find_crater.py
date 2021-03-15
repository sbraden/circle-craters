import numpy as np
import requests

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
        self.b = y + (r_in - y)
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