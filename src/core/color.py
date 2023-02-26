import math
import pyglet
import numpy as np

class ColorPicker:
    """
    Probably needs some cleanup was kinda patched together
    """
    def __init__(self, window, x, y, diameter=100):
        self.window = window
        self._x, self._y = x, y
        self.diameter = diameter/2


        #State Variables
        self.onCircle = False
        self.onTriangle = None


        self._vertlist = set()
        self._root = pyglet.graphics.Group()
        fgroup = pyglet.graphics.OrderedGroup(3, parent=self._root)
        lgroup = pyglet.graphics.OrderedGroup(1, parent=self._root)
        igroup = pyglet.graphics.OrderedGroup(2, parent=self._root)
        bgroup = pyglet.graphics.OrderedGroup(0, parent=self._root)
        self._batch = pyglet.graphics.Batch()

        #Triangle Coordinations (Equilateral)
        x1, y1 = x, y
        x2, y2 = x+diameter//2, (diameter**2 - (diameter/2)**2)**(1/2) + y1
        x3, y3 = x+diameter, y

        self.selector = pyglet.shapes.Triangle(x1, y1, x2, y2, x3, y3, group=fgroup, batch=self._batch)
        self.selector._vertex_list.colors = [255,255,255,255, 0,0,0,255, 0,0,0,255]

        cx = (x1+x2+x3)/3
        cy = (y1+y2+y3)/3

        self.circle = pyglet.shapes.Circle(cx, cy, diameter/2, segments=180, color=(0,0,0), group=bgroup, batch=self._batch)
        correction = y2 - (self.circle.y + diameter/2)
        self.circle.radius += correction

        self._inner = pyglet.shapes.Circle(self.circle.x, self.circle.y, self.circle.radius, segments = 180, color=(125,125,125), group=igroup, batch=self._batch)
        self.circle.radius += 20

        self.line = pyglet.shapes.Line(cx, cy, cx+self.circle.radius, cy, width=1, color=(255,255,255), group=lgroup, batch=self._batch)


        view_x, view_y = self.circle.x+self.circle.radius, self.circle.y-self.circle.radius
        size_x, size_y = [diameter/5]*2
        self.viewbox = pyglet.shapes.Rectangle(view_x-size_x, view_y, size_x, size_y, color=(0,0,0), group=bgroup, batch=self._batch)
        self.delta_triangle = 0, 0
        self.focus = False #To know if it's being interact with

        self.dLine = pyglet.shapes.Line(0,0,-1,-1, width=1, color=(255,255,255))

        self.circleList = [
                pyglet.shapes.Circle(0, 0, 2, color=(255,0,0)),
                pyglet.shapes.Circle(0, 0, 2, color=(0,255,0)),
                pyglet.shapes.Circle(0, 0, 2, color=(0,0,255))
        ]



        chunk = int(self.circle._segments//6) #Red, Yellow, Green, Cyan, Blue, Pink
        self.chunks = {
            "Red"       : [0, chunk],
            "Yellow"    : [chunk, chunk*2],
            "Green"     : [chunk*2, chunk*3],
            "Cyan"      : [chunk*3, chunk*4],
            "Blue"      : [chunk*4, chunk*5],
            "Pink"      : [chunk*5, chunk*6],
        }

        self.color = {
            "Red"   : [255,0,0,255],
            "Yellow": [255,255,0,255],
            "Green" : [0,255,0,255],
            "Cyan"  : [0,255,255,255],
            "Blue"  : [0,0,255,255],
            "Pink"  : [255,0,255,255],
        }
        icolor = iter(self.color); next(icolor) #Iter Colors
        self.select_color = [0,0,0,255]

        for key, value in self.chunks.items():
            try: n_color = next(icolor) #Next Color
            except: n_color = "Red"

            for index in range(*value):
                start = index*12
                end = start+12

                curr_c = self.color[key]
                next_c = self.color[n_color]
                fraction = (index-value[0])/chunk
                lerp_c = [
                        self.lerp(curr_c[0], next_c[0], fraction),
                        self.lerp(curr_c[1], next_c[1], fraction),
                        self.lerp(curr_c[2], next_c[2], fraction),
                        255
                ]
                #if key == "Red": print(lerp_c, end="; ")
                self.circle._vertex_list.colors[start:end] = lerp_c*3

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        dx = value - self._x
        self._x += dx
        self.selector.x += dx
        self.selector.x2 += dx
        self.selector.x3 += dx
        self.circle.x += dx
        self._inner.x += dx
        self.viewbox.x += dx
        self.line.x = self._inner.x
        self.line.x2 += dx

    @y.setter
    def y(self, value):
        dy = value - self._y
        self._y += dy
        self.selector.y += dy
        self.selector.y2 += dy
        self.selector.y3 += dy
        self.circle.y += dy
        self._inner.y += dy
        self.viewbox.y += dy
        self.line.y = self._inner.y
        self.line.y2 += dy

    @property
    def visible(self):
        return self._root.visible

    @visible.setter
    def visible(self, value):
        self._root.visible = value

    def set_color(self, color):
        self.select_color = color
        self.selector._vertex_list.colors[8:12] = color
        self.delta_triangle = (0,0)
        self.triangle_color()

    def lerp(self, a, b, c):
        """
        Thank you StackOverflow
        """
        return int(a*(1-c)+(b*c))

    def get_color(self):
        bcolor = bytes(self.triangle_color())
        ncolor = np.frombuffer(bcolor, dtype=np.uint32)[0]
        return ncolor

    def triangle_color(self, x=None, y=None):
        """
        Barycentric whatchamacalit I got from the Internet to get the
        `weight` of each vertices
        """

        if x: dx = x - self.selector.x3
        else: dx = self.delta_triangle[0]

        if y: dy = y - self.selector.y3
        else: dy = self.delta_triangle[1]

        x = self.selector.x3 + dx
        y = self.selector.y3 + dy

        color1 = [255,255,255,255]
        color2 = [0, 0, 0, 255]
        color3 = self.select_color

        #Weight of each vertices
        x1, y1, x2, y2, x3, y3 = self.selector._vertex_list.vertices[:]
        px, py = x, y

        DN = (y2-y3)*(x1 - x3) + (x3-x2)*(y1-y3)
        W1 = ((y2-y3)*(px-x3) + (x3-x2)*(py-y3))/DN #White
        W2 = ((y3-y1)*(px-x3) + (x1-x3)*(py-y3))/DN #Black
        W3 = 1 - W1 - W2 #Red

        color = [
           int(color1[0]*W1+color2[0]*W2+color3[0]*W3),
           int(color1[1]*W1+color2[1]*W2+color3[1]*W3),
           int(color1[2]*W1+color2[2]*W2+color3[2]*W3),
           255,
        ]

        self.delta_triangle = (dx, dy)

        return color

        #print(color)
        #print("Weight 1: %.2f; Weight 2: %.2f; Weight3: %.2f"%(W1, W2, W3))

    def in_triangle(self, x, y):

        def area(x1, y1, x2, y2, x3, y3):
            """
            Matrices oh yes
            """
            return abs((x1*(y2-y3)) + (x2*(y3-y1)) + (x3*(y1-y2)))/2

        
        x1, y1, x2, y2, x3, y3 = self.selector._vertex_list.vertices[:]


        A1 = area(x1, y1, x2, y2, x, y) #1,2,P
        A2 = area(x1, y1, x3, y3, x, y) #1,3,P
        A3 = area(x2, y2, x3, y3, x, y) #2,3,P

        Area = area(x1, y1, x2, y2, x3, y3)
        PArea = A1+A2+A3


        return PArea == Area



    def in_selector(self, x, y):
        x1, y1 = self.circle.x, self.circle.y
        x2, y2 = x, y

        hypoth = pow(pow((x2-x1), 2) + pow((y2-y1), 2), 1/2)
        if hypoth > self.circle.radius or hypoth < self._inner.radius or hypoth == 0:
            return False
        return True

    def _get_color(self, x, y):

        if not self.in_selector(x, y): return self.select_color
        x1, y1 = self.circle.x, self.circle.y
        x2, y2 = x, y

        hypoth = pow(pow((x2-x1), 2) + pow((y2-y1), 2), 1/2)
        angle = math.acos((x2-x1)/hypoth) if y > y1 else 2*math.pi - math.acos((x2-x1)/hypoth) #Correcting angle
        angle = angle/(2*math.pi) * 6 #Normalize and setup for 6 sections

        index = int(angle)
        lcolors = list(self.chunks)
        c_color = self.color[lcolors[index]]

        nindex = index+1 if index < len(lcolors)-1 else 0
        n_color = self.color[lcolors[nindex]]

        #Interpolation oh yes
        color = [
            self.lerp(c_color[0], n_color[0], angle-index),
            self.lerp(c_color[1], n_color[1], angle-index),
            self.lerp(c_color[2], n_color[2], angle-index),
            255,
        ]

        return color

    def clamp_triangle(self, x, y):
        """
        Function to limit the points to the triangle borders
        TODO:
         - Find a way to get the intersection between 2 lines so
           it gives the triangle point
        """
        x1, y1, x2, y2, x3, y3 = self.selector._vertex_list.vertices[:]

        line1 = (np.asarray([x1, y1]), np.asarray([x2, y2]))
        line2 = (np.asarray([x2, y2]), np.asarray([x3, y3]))
        line3 = (np.asarray([x3, y3]), np.asarray([x1, y1]))

        def line_intersect(lineA, lineB, hint):
            """
            Got this from StackOverflow
            """
            p1_start = lineA[0]
            p1_end = lineA[1]

            p2_start = lineB[0]
            p2_end = lineB[1]

            p = p1_start
            r = (p1_end-p1_start)

            q = p2_start
            s = (p2_end-p2_start)

            t = np.cross(q-p,s)/(np.cross(r,s))
            i = p + t*r

            hint.x = i[0]
            hint.y = i[1]
            return i[0], i[1]


        dline   = (np.asarray([self.onTriangle[0], self.onTriangle[1]]), np.asarray([x, y]))

        RPoint  = line_intersect(line1, dline, self.circleList[0]) #Red
        GPoint  = line_intersect(line2, dline, self.circleList[1])
        BPoint  = line_intersect(line3, dline, self.circleList[2])

        RVector = np.array([RPoint[0]-self.onTriangle[0], RPoint[1]-self.onTriangle[1]]) 
        GVector = np.array([GPoint[0]-self.onTriangle[0], GPoint[1]-self.onTriangle[1]]) 
        BVector = np.array([BPoint[0]-self.onTriangle[0], BPoint[1]-self.onTriangle[1]]) 

        DVector = np.array([x-self.onTriangle[0], y-self.onTriangle[1]])

        RVector /= np.linalg.norm(RVector); GVector /= np.linalg.norm(GVector)
        BVector /= np.linalg.norm(BVector); DVector /= np.linalg.norm(DVector)

        def ROUND(_nparray, precision):
            return np.array([ round(_nparray[0], precision), round(_nparray[1], precision) ])

        RVector = ROUND(RVector, 3); BVector = ROUND(BVector, 3)
        GVector = ROUND(GVector, 3); DVector = ROUND(DVector, 3)

        #print("\nDVector:",DVector, "\nRVector:", RVector, "\nGVector:",GVector,"\nBVector:",BVector)

    
        if DVector.tolist() == BVector.tolist() and BPoint[0] > x1 and BPoint[0] < x3: return BPoint
        if DVector.tolist() == RVector.tolist() and x < x2 and RPoint[0] < x2: return RPoint
        if DVector.tolist() == GVector.tolist() and x > x2 and GPoint[0] > x2: return GPoint
        


        return x2, y2




    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):


        if self.onTriangle:
            tx, ty = x, y
            if not self.in_triangle(x, y):
                tx, ty = self.clamp_triangle(x, y)


            self.dLine.x2 = x
            self.dLine.y2 = y
            self.triangle_color(tx, ty)
            return
            #print(x, y, tx, ty)
            #print(tx, ty)
            #self.triangle_color(int(tx), int(ty))


        if self.onCircle:
            cx, cy = self.circle.x, self.circle.y
            dx, dy = x-cx, y-cy

            dist = pow(pow(dx, 2)+ pow(dy, 2), 1/2)
            angle = math.acos(dx/dist)
            if dy < 0: angle = 2*math.pi-angle

            self.line.x2 = self.line.x + self.circle.radius *math.cos(angle)
            self.line.y2 = self.line.y + self.circle.radius *math.sin(angle)
            self.delta_triangle = (0, 0)
            self.select_color = self._get_color(self.line.x2, self.line.y2)
            self.selector._vertex_list.colors[8:12] = self.select_color


    def on_mouse_release(self, x, y, button, modifiers):
        self.focus = False
        self.onCircle = False
        self.onTriangle = False

    def on_mouse_press(self, x, y, button, modifiers):
        self.onCircle = False
        self.onTriangle = None

        if not self.visible: return
        if self.in_triangle(x, y):
            self.focus = True
            self.triangle_color(x, y)
            self.onTriangle = [float(x), float(y)]

            self.dLine.x = x
            self.dLine.y = y
            self.dLine.x2, self.dLine.y2 = self.onTriangle
            return

        if self.in_selector(x, y):
            self.focus = True
            self.onCircle = True
            self.delta_triangle = (0, 0)
            self.select_color = self._get_color(x, y)
            self.selector._vertex_list.colors[8:12] = self.select_color

    def draw(self):
        self._batch.draw()
        self.viewbox.color = self.triangle_color()[0:3]
        #for point in self.circleList: point.draw()

        if self.onTriangle: self.dLine.draw()


