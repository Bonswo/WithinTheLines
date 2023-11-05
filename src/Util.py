import math

def get_polyline_points(start, end, width):
    x0, y0 = start
    x1, y1 = end
    if y1 == y0:
        return(start, start, end, end)

    rad_angle = math.atan(-(x1-x0)/(y1-y0))
    p1 = (x0 - math.cos(rad_angle) * width/2, y0 - math.sin(rad_angle) * width/2)
    p2 = (x0 + math.cos(rad_angle) * width/2, y0 + math.sin(rad_angle) * width/2)
    
    p3 = (x1 + math.cos(rad_angle) * width/2, y1 + math.sin(rad_angle) * width/2)
    p4 = (x1 - math.cos(rad_angle) * width/2, y1 - math.sin(rad_angle) * width/2)
    return (p1, p2, p3, p4)