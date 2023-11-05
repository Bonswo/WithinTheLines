import numpy, math
from .Util import get_polyline_points

class BoundingBox():
    def __init__(self, start, end, width=100) -> None:
        self.width = width
        self.start = start
        self.end = end
        self.points = get_polyline_points(self.start, self.end, self.width)
        self.min_x = min([x for (x,y) in self.points])
        self.min_y = min([y for (x,y) in self.points])
        self.max_x = max([x for (x,y) in self.points])
        self.max_y = max([y for (x,y) in self.points])
    
    def min_distance_to_point(self, point):
        x1, y1 = self.start
        x2, y2 = self.end
        x0, y0 = point
        nominator = abs((x2 - x1)*(y1-y0)-(x1-x0)*(y2-y1))
        denominator = numpy.sqrt((x2-x1)**2+(y2-y1)**2)
        distance = nominator/denominator - self.width/2
        return distance

    def point_inside_box(self, point):
        x0, y0 = point
        inside_line = False
        if x0 > self.min_x and x0 < self.max_x and y0 > self.min_y and y0 < self.max_y:
            inside_line = self.min_distance_to_point(point) <= 0
        
        inside_start = math.sqrt((self.start[1]-y0)**2+(self.start[0]-x0)**2) < self.width/2
        inside_end = math.sqrt((self.end[1]-y0)**2+(self.end[0]-x0)**2) < self.width/2

        return inside_start or inside_end or inside_line
        
    def get_info(self):
        return {'start': self.start,
                'end' : self.end,
                'width' : self.width,
                'points' : self.points}

    def point_distance_to_end(self, point):
        x0, y0 = point
        x1, y1 = self.end
        distance = numpy.sqrt(abs((y1-y0)**2+(x1-x0)**2)) - self.width/2

        return distance