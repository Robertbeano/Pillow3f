from PIL import Image
from itertools import product
from math import cos, sin, atan, radians, degrees, pi, tan, acos, asin
import numpy

class RenderPipeline:
    def __init__(self, window_w, window_h):
        self.parent_map = Image.new('RGBA', (window_w, window_h))
        self.bitmap = self.parent_map.load()
        self.height = window_h
        self.width = window_w
        self.camera = [[0, 0, -20], [0, 0, 0]]
        self.fov = 45

    def save(self, file_type, location, name):
        self.parent_map.save(location + '/' + name + '.' + file_type)
        
    def subdivide(self, v1, v2, v3):
        avgs = [sum(x)/3 for x in list(zip(v2, v2, v3))]
        return [(avgs, v1, v2), (avgs, v2, v3), (avgs, v1, v3)]

    def pixel(self, x, y, color_data):
        x, y = int(x), int(y)
        if x in range(-self.width//2+1, self.width//2-1) and y in range(-self.height//2+1, self.height//2-1):
            self.bitmap[int(x+(self.width/2)), int((-y)+(self.height/2))] = color_data

    def project(self, vert, cam, camera_rotation, fov):
        vert = numpy.multiply(vert, 3)
        Cx, Cy, Cz, Sx, Sy, Sz = [cos(radians(x)) for x in camera_rotation] + [sin(radians(x)) for x in camera_rotation]
        rotation_matrix = numpy.dot(numpy.dot(
            [[1, 0, 0],
             [0, Cx, -Sx],
             [0, Sx, Cx]],

            [[Cy, 0, Sy],
             [0,  1, 0],
             [-Sy, 0, Cy]]),

            [[Cz, -Sz, 0],
             [Sz, Cz, 0],
             [0, 0, 1]])
        
        f = (fov*(45/26))/45
        new_vert = numpy.subtract(cam, vert)
        dx, dy, dz = numpy.dot(rotation_matrix, new_vert)
        dz = dz * f
        aspect = self.width/self.height
        return (dx/dz)*self.width, (dy/dz)*self.height*aspect
    
    def relative(self, x):
        return [j/max(x) for j in x]

    def totalic(self, x):
        return [j/sum(x) for j in x]

    def softmax(self, x):
        return numpy.exp(x)/numpy.sum(numpy.exp(x))
    
    def angle(self, *args):
        if len(args) == 3:
            v1, v2, v3 = args
            refrence = sorted([v1, v2, v3], key=lambda x: x[1])[::-1]
            point1 = numpy.add(refrence[0], 0)
            point2 = numpy.add(numpy.divide(numpy.add(refrence[1], refrence[2]), 2), 0)
            Ax, Ay, Az = point1
            Bx, By, Bz = point2
            Cx, Cy, Cz = refrence[1]
            Dx, Dy, Dz = refrence[2]
            if Cz-Dz == 0:
                slopex = 999999
            else:
                slopex = (Cx-Dx)/(Cz-Dz)

            if Cx-Dx == 0:
                slopey = 999999
            else:
                slopey = (Cy-Dy)/(Cx-Dx)

            if Ax-Bz == 0:
                slopez = 0
            else:
                slopez = (Az-Bz)/(Ay-By)
            return round(90-degrees(atan(slopex)), 3), round(degrees(atan(slopey)), 3), round(degrees(atan(slopez)), 3)

    def vertex(self, vert, color):
        x, y = self.project(vert, self.camera[0], self.camera[1], self.fov)
        self.pixel(x, y, color)

    def distance2(self, x1, y1, x2, y2):
        return ((x1-x2)**2+(y1-y2)**2)**(1/2)

    def intrange(self, one, two):
        temp = list()
        if one==two:
            return [one,]
        else:
            h=0
            for h in range(abs(one-two)+1):
                if two<one:
                    temp.append(one-h)
                if two>one:
                    temp.append(one+h)
        return temp
        
        
    def triangle(self, verts, color, shading='totalic', exponent=1.6):
        color = [[y*255 for y in x] for x in color]
        if shading == 'relative':
            color_type = self.relative
        if shading == 'totalic':
            color_type = self.totalic
        if shading == 'softmax':
            color_type = self.softmax
        A, B, C = [self.project(vert, self.camera[0], self.camera[1], self.fov) for vert in verts]
        Ax, Ay, Bx, By, Cx, Cy = [int(y) for y in A + B + C]
        lineBC = self.stretch(self.intrange(Bx, Cx), self.intrange(By, Cy))
        lineAC = self.stretch(self.intrange(Ax, Cx), self.intrange(Ay, Cy))
        for x1, y1, x2, y2 in zip(*lineBC, *lineAC):
            x1, y1, x2, y2 = [int(z) for z in (x1, y1, x2, y2)]
            fill_line = self.stretch(self.intrange(x1, x2), self.intrange(y1, y2))
            for fx, fy in zip(*fill_line):
                Aperc = (self.distance2(fx, fy, Ax, Ay)+1)**-exponent
                Bperc = (self.distance2(fx, fy, Bx, By)+1)**-exponent
                Cperc = (self.distance2(fx, fy, Cx, Cy)+1)**-exponent
                profile = [numpy.multiply(p, c) for p, c in zip(color_type([Aperc, Bperc, Cperc]), color)]
                c_color = [int(x) for x in numpy.add(numpy.add(profile[0], profile[1]), profile[2])]
                self.pixel(fx, fy, tuple(c_color))

    def quad(self, verts, color):
        A, B, C, D = [self.project(vert, self.camera[0], self.camera[1], self.fov) for vert in verts]
        Ax, Ay, Bx, By, Cx, Cy, Dx, Dy = [int(y) for y in A + B + C + D]
        lineAB = self.stretch(self.intrange(Ax, Bx), self.intrange(Ay, By))
        lineCD = self.stretch(self.intrange(Cx, Dx), self.intrange(Cy, Dy))
        for x1, y1, x2, y2 in zip(*lineAB, *lineCD):
            x1, y1, x2, y2 = [int(z) for z in (x1, y1, x2, y2)]
            fill_line = self.stretch(self.intrange(x1, x2), self.intrange(y1, y2))
            for fx, fy in zip(*fill_line):
                Aperc = (self.distance2(fx, fy, Ax, Ay)+1)**-3
                Bperc = (self.distance2(fx, fy, Bx, By)+1)**-3
                Cperc = (self.distance2(fx, fy, Cx, Cy)+1)**-3
                Dperc = (self.distance2(fx, fy, Dx, Dy)+1)**-3
                profile = [numpy.multiply(p, c) for p, c in zip(self.softmax([Aperc, Bperc, Cperc, Dperc]), color)]
                c_color = [int(x) for x in numpy.add(numpy.add(numpy.add(profile[0], profile[1]), profile[2]), profile[3])]
                self.pixel(fx, fy, tuple(c_color))
            
    def rotate(self, vert, rot):
        Cx, Cy, Cz, Sx, Sy, Sz = [cos(radians(x)) for x in rot] + [sin(radians(x)) for x in rot]
        return numpy.dot(numpy.dot(numpy.dot(
        [[1, 0, 0],
         [0, Cx, -Sx],
         [0, Sx, Cx]],
        
        [[Cy, 0, Sy],
         [0, 1, 0],
         [-Sy, 0, Cy]]),

        [[Cz, -Sz, 0],
         [Sz, Cz, 0],
         [0, 0, 1]]), vert)

    def stretch(self, *lists):
        lists = [list(l) for l in lists]
        length = max([len(l) for l in lists])
        return [[l[i * len(l) // length] for i in range(length)]
                for l in lists]
            


            
        
if __name__ == '__main__':
    import time
    Pipe = RenderPipeline(600, 800)
    verts = [-5, -2.5, 0], [5, -2.5, 0], [-5, 5, 0]
    colors = [[1, 0, 0], [0, 0, 1], [0, 1, 0]]
    print(colors)
    Pipe.triangle(verts, colors)
    Pipe.save(location='C:/', name='image%s'%int(time.time()), file_type='png')
    Pipe.parent_map.show()
