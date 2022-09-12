"""
Version 0.0b will include the following features:
-Brush Tool (Done)
-Eraser tool (Done)
-Fill Tool(Done)
-5 colors: (Done)
 - Red
 - Blue
 - Green
 - White
 - Black
-Redo and Undo (Done)

**(Future Features for version 0.0)**
-An actual GUI
 - Toolbar
 - Statusbar (for tooltip and etc, like Pencil2D's)
 - Buttons
 - More stuff

-Image layers
-Import Images
-Color selector
-Tools THICCness
-Change resolution
-Selection tool (probably)
-Different image export type
-Hitman's eraser (erase specific color)

**more features might be added in the future**
"""

import numpy as np
import pyglet,numba
from pyglet.gl import*
from pyglet.window import key

#Window constants
WIDTH, HEIGHT = 1280, 720
BGCOLOR = (.7,.7,.7,1)

window = pyglet.window.Window(
    WIDTH, HEIGHT,
    caption = "Simple Paint"
)

#Color Palettes
WHITE = np.array([255,255,255,255])
BLACK = np.array([0,0,0,255])
RED   = np.array([255,0,0,255])
GREEN = np.array([0,255,0,255])
BLUE  = np.array([0,0,255,255])

#Canvas varibales
CWIDTH, CHEIGHT = 800, 600
canvas_x, canvas_y = 0, 0
c_data = np.zeros((CHEIGHT, CWIDTH, 4), dtype='uint8')

ur_max = 24
ur_data, ur_index = [None]*ur_max, 0 #Undo-Redo data

#Tools variable
toolMode = 0
"""
B(0) : Brush
F(1) : Bucket
E(2) : Eraser
"""
paintColor = BLACK
zoom, zoomMin, zoomMax = 1, 0.1, 5

#Tool functions
@numba.njit
def colors_equal(color1, color2):
    for val1, val2 in zip(color1, color2):
        if val1 != val2: return False
    return True

@numba.njit
def set_color(old_color, new_color):
    for i in range(len(old_color)):
        old_color[i] = new_color[i]

@numba.njit
def fill(data, x, y, fillColor):
    height, width, _ = data.shape
    p_color = np.copy(data[y][x])
    queue = []
    queue.append((x, y))
    visited = set()
    
    while len(queue):
        x, y = queue.pop()
        if in_canvas(x, y) and colors_equal(data[y][x], p_color) and (x, y) not in visited:
            visited.add((x, y))
            set_color(data[y][x], fillColor)

            queue.append((x+1, y))
            queue.append((x-1, y))
            queue.append((x, y+1))
            queue.append((x, y-1))

@numba.njit
def in_canvas(x, y):
    if x < canvas_x or x >= CWIDTH+canvas_x or y < canvas_y or y >= CHEIGHT+canvas_y:
        return False
    return True

@numba.njit
def zoom_coords(x, y, zoom):
    return int(x/zoom), int(y/zoom)

@numba.njit
def draw(x, y, c_data, last_mouse, zoom, drawColor):
    #Corners correction
    dx=x-last_mouse[0]
    dy=y-last_mouse[1]
    
    if not dx and not dy: return

    if in_canvas(*last_mouse):
        if not in_canvas(x, 0):
            if x > CWIDTH//2: x=CWIDTH-1
            if x < CWIDTH//2: x=0
        
        if not in_canvas(0, y):
            if y > CHEIGHT//2: y=CHEIGHT-1
            if y < CHEIGHT//2: y=0

    if not in_canvas(x, y): return
    adx, ady = abs(dx), abs(dy)
    dist = (adx**2 + ady**2)**(1/2)
    
    for i in range(adx):
        cy = last_mouse[1]+round(dy*(i/adx))
        cx = last_mouse[0]+i
        if dx < 0: cx = last_mouse[0]-i #Opposite side

        if in_canvas(cx, cy): c_data[int(cy), int(cx)] = drawColor #Draw if in canvas

    for j in range(ady):
        cx = last_mouse[0]+round(dx*(j/ady))
        cy = last_mouse[1]+j
        if dy < 0: cy = last_mouse[1]-j #Opposite side

        if in_canvas(cx, cy): c_data[int(cy), int(cx)] = drawColor #Draw if in canvas

def clear():
    global c_data
    c_data = np.ones([CHEIGHT, CWIDTH, 4], dtype='uint8')
    c_data = np.multiply(c_data, 255)
    updateURData()

def resetCanvas():
    global canvas_x, canvas_y, zoom
    canvas_x =WIDTH//2; canvas_y=HEIGHT//2; zoom=1 #Reseting position

def zoomCanvas(x, y, scroll_y):
    global canvas_x, canvas_y, zoom
   
    #Recording old dimensions and modify zoom
    oldWidth, oldHeight = CWIDTH * zoom, CHEIGHT *zoom
    zoom = min(max(zoom+scroll_y/10, zoomMin), zoomMax)

    #Zoom focus!!!
    newWidth, newHeight = CWIDTH*zoom, CHEIGHT*zoom
    pWidth, pHeight     = newWidth/oldWidth, newHeight/oldHeight #Percentage
    deltaX, deltaY      = (x - canvas_x)*pWidth, (y-canvas_y)*pHeight
    canvas_x, canvas_y  = x - deltaX, y - deltaY

def updateURData():
    global ur_index, ur_data
   
    #Poping out if maximum reached
    if ur_index == ur_max-1:
        ur_data.append(None)
        ur_data.pop(0)
        ur_index -= 1 
    
    if ur_index == None: ur_index = 0
    else: ur_index += 1

    #Clearing Redo values
    if ur_index < ur_max-1:
        for x in range(ur_index, ur_max-1):
            ur_data[x] = None

    ur_data[ur_index] = np.copy(c_data)

def undo():
    global c_data, ur_data, ur_index

    
    if ur_index == None or ur_index == 0:
        print("Cannot undo: minimum reached"); return

    ur_index -= 1
    c_data = np.copy(ur_data[ur_index])

def redo():
    global c_data, ur_data, ur_index

    if ur_index == None or ur_index+1 == ur_max or ur_data[ur_index+1] is None:
        print("Cannot redo: maximum reached"); return

    ur_index += 1
    c_data = np.copy(ur_data[ur_index])

def save():
    #Converting to texture
    saveImg = c_data.tobytes()
    saveImg = pyglet.image.ImageData(CWIDTH, CHEIGHT, 'RGBA', saveImg)
    
    saveImg.save("Untitled.png")
    print(CSI+"33m"+"Image saved in current directory as \"Untitled.png\" "+CSI+"0m")

last_mouse = None
@window.event
def on_mouse_press(x, y, bttn, mod):
    global last_mouse

    #Position conversion
    x = x-canvas_x+CWIDTH//2*zoom; y = y-canvas_y+CHEIGHT//2*zoom

    if bttn != 1: return
    last_mouse = zoom_coords(x, y, zoom)
    if toolMode == 1: 
        fill(c_data, *last_mouse, paintColor)
        updateURData()

#Make sure to change it when adding gui so undo redo is
#updated when drawing only (create a 'drawing' variable)

@window.event
def on_mouse_release(x, y, bttn, mod):
    if bttn == 1 and toolMode == 0: updateURData()

@window.event
def on_mouse_drag(x, y, dx, dy, bttn, mod):
    global last_mouse, canvas_x, canvas_y

    #Moving canvas
    if bttn ==2: canvas_x += dx; canvas_y += dy

    #Position conversion
    if toolMode != 0 and toolMode != 2: return
    x = x-canvas_x+CWIDTH//2*zoom; y = y-canvas_y+CHEIGHT//2*zoom
    x, y = zoom_coords(x, y, zoom)
    if bttn == 1: 
        if toolMode == 0: draw(x, y, c_data, last_mouse, zoom, paintColor)
        if toolMode == 2: draw(x, y, c_data, last_mouse, zoom, WHITE)

    last_mouse = x, y

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    zoomCanvas(x, y, scroll_y)

@window.event
def on_key_press(symbol, mod):
    global canvas_x, canvas_y, zoom
    global toolMode, paintColor

    if mod & key.MOD_CTRL:
        if symbol == key._1: paintColor = BLACK; print("Paint Color: Black")
        if symbol == key._2: paintColor = WHITE; print("Paint Color: White")
        if symbol == key._3: paintColor = RED; print("Paint Color: Red")
        if symbol == key._4: paintColor = GREEN; print("Paint Color: Green")
        if symbol == key._5: paintColor = BLUE; print("Paint Color: Blue")

        #Undo and redo
        if symbol == key.Z: undo()
        if symbol == key.Y: redo()
        if symbol == key.S: save()


    if key.C == symbol: clear()
    #Changing tool mode
    if key.B == symbol: toolMode = 0; print("Tool Mode: Brush")
    if key.F == symbol: toolMode = 1; print("Tool Mode: Bucket")
    if key.E == symbol: toolMode = 2; print("Tool Mode: Eraser")
    if key.R == symbol: resetCanvas() #Reseting position

@window.event
def on_draw():
    #Data conversion
    output = c_data.tobytes()
    output = pyglet.image.ImageData(CWIDTH, CHEIGHT, 'RGBA', output)
    output = output.get_texture()

    glClearColor(*BGCOLOR)
    
    #Smoothing only if far
    if zoom > 1:
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) #Disable Smoothing
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) #Disable Smoothing

    window.clear()

    output.width = int(CWIDTH*zoom)
    output.height = int(CHEIGHT*zoom)
    output.anchor_x = output.width//2
    output.anchor_y = output.height//2
    output.blit(canvas_x, canvas_y)

CSI = "\x1B["
#Compiling numba functions in advance
def numba_funcs():
    global canvas_x, canvas_y, ur_index
    print(CSI+"32m" + "Loading functions..." + CSI + "0m")
    fill(c_data, 0, 0, WHITE)
    draw(0,0,c_data,(0,0,), zoom, paintColor)
    clear()
    
    ur_data[0] = np.copy(c_data); ur_index = 0 #Initial undo redo state
    canvas_x, canvas_y = WIDTH//2, HEIGHT//2 #Initial position at center
    print(CSI+"32m" + "Done!" + CSI + "0m")

#Startup setup
numba_funcs()
pyglet.app.run()
print("Bye")
