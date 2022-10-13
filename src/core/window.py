"""
Module for calling the basic functions of
window the main things will be done inside
'main.py' file. This is the script that links
to other scripts
"""

import pyglet
from pyglet.gl import*
from pyglet.window import key

import src.core.canvas as canvas
import src.tools.ids as toolID
import src.core.dhist as dhist
import src.core.mouse as mouse
import src.cfuncs as clib
import numpy as np

#Colors
WHITE   = 0xFFFFFFFF
BLACK   = 0xFF000000
RED     = 0xFF0000FF
GREEN   = 0xFF00FF00
BLUE    = 0xFFFF0000

KEYBOARD = key.KeyStateHandler()
BGCOLOR = [.7, .7, .7 , 1]

#Window
window = pyglet.window.Window(800, 600, caption="Simple - Paint")
brush_size = 0
color = BLACK


#Initializing canvas
canvas.x, canvas.y = window.width//2, window.height//2
canvas.set_size(640, 480); canvas.data.fill(WHITE)

#Initializing draw history module
dhist.data[dhist.index] = np.copy(canvas.data)
dhist.index = 0

def save():
    save_img = canvas.data.tobytes()
    save_img = pyglet.image.ImageData(canvas.width, canvas.height, 'RGBA', save_img)

    save_img.save("Untitled.png")
    print("[Image saved as \"Untitled.png\" in current directory]")

def draw(x, y, mx, my):
    if mouse.target_gui: return
    dcolor = color
    target = toolID.MODULES[mouse.tool]
    if mouse.tool == toolID.ERASER: dcolor = WHITE
    clib.draw(dcolor, target.size, x, y, mx, my)

def flood_fill(x, y): 
	if mouse.target_gui: return
	clib.flood_fill(color, x, y); dhist.update()

def tool_mode(ID):
    mouse.set_toolmode(ID)

def set_color(ncolor):
    global color
    color = ncolor
    print("Color set to: ", end="")
    if color == BLACK: print("Black")
    if color == WHITE: print("White")
    if color == RED: print("Red")
    if color == GREEN: print("Green")
    if color == BLUE: print("Blue")

def zoom(x, y, scroll_y):
    old_width, old_height = canvas.width*canvas.zoom, canvas.height*canvas.zoom
    canvas.zoom = min(max(canvas.zoom+scroll_y/10, canvas.min_zoom), canvas.max_zoom)
        
    #Moving canvas
    new_width, new_height = canvas.width*canvas.zoom, canvas.height*canvas.zoom
    per_width, per_height = new_width/old_width, new_height/old_height #Percentage
    delta_x, delta_y      = (x-canvas.x)*per_width, (y-canvas.y)*per_height
    canvas.x, canvas.y    = x-delta_x, y-delta_y

def set_brush_size(size): 
    target = toolID.MODULES[mouse.tool]
    target.size = min(max(target.MIN_SIZE, size), target.MAX_SIZE)
    print("Brush size is not: %d"%(target.size))

#MOUSE EVENTS#
@window.event
def on_mouse_press(x, y, bttn, mod):
    if bttn == 1 and mouse.tool == toolID.BUCKET:
        flood_fill(x, y)
    mouse.x, mouse.y = x, y

@window.event
def on_mouse_release(x, y, bttn, mod):
    if (mouse.tool == toolID.PENCIL or mouse.tool == toolID.ERASER) and bttn == 1: dhist.update()

@window.event
def on_mouse_drag(x, y, dx, dy, bttn, mod):
    if (mouse.tool == toolID.PENCIL or mouse.tool == toolID.ERASER) and bttn == 1:
        draw(x, y, mouse.x, mouse.y)

    mouse.x, mouse.y = x, y
    if bttn == 2: canvas.x += dx; canvas.y += dy

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if KEYBOARD[key.LSHIFT] and mouse.tool in toolID.RESIZABLES:
        if scroll_y > 0: set_brush_size(toolID.MODULES[mouse.tool].size+1)
        else: set_brush_size(toolID.MODULES[mouse.tool].size - 1)
    
    else: zoom(x, y, scroll_y)
    
@window.event
def on_mouse_motion(x, y, dx, dy):
	mouse.x, mouse.y = x, y

#KEYBOARD EVENTS#
@window.event
def on_key_press(symbol, mod):
    """
    Function for key shortcuts
    """
    if mod & key.MOD_CTRL:
        if symbol == key.S: save()
        if symbol == key.Z: 
            if KEYBOARD[key.LSHIFT]: dhist.redo()
            else: dhist.undo()

        if symbol == key._1: set_color(BLACK)
        if symbol == key._2: set_color(WHITE)
        if symbol == key._3: set_color(RED)
        if symbol == key._4: set_color(GREEN)
        if symbol == key._5: set_color(BLUE)

    #Reset canvas
    if symbol == key.R:
        canvas.zoom = 1
        canvas.x = window.width//2
        canvas.y = window.height//2

    if symbol == key.B: tool_mode(toolID.PENCIL)
    if symbol == key.F: tool_mode(toolID.BUCKET)
    if symbol == key.C: canvas.data.fill(WHITE); dhist.update()
    if symbol == key.E: tool_mode(toolID.ERASER)

@window.event
def on_draw():
    output = canvas.data.tobytes()
    output = pyglet.image.ImageData(canvas.width, canvas.height, 'RGBA', output)
    output = output.get_texture()

    glClearColor(*BGCOLOR)

    if canvas.zoom > 1:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
    window.clear()
    output.width = int(canvas.width*canvas.zoom)
    output.height = int(canvas.height*canvas.zoom)
    output.anchor_x = output.width//2
    output.anchor_y = output.height//2
    output.blit(canvas.x, canvas.y)


def update(dt): pass

window.push_handlers(KEYBOARD)
#pyglet.clock.schedule_interval(update, 1/60)
