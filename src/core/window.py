"""
Module for calling the basic functions of
window the main things will be done inside
'main.py' file. This is the script that links
to other scripts
"""

import time
import pyglet
from pyglet.gl import*
from pyglet.window import key

import src.core.canvas as canvas
import src.core.dhist as dhist
import src.core.mouse as mouse
import src.cfuncs as clib
import src.gui as gui
import numpy as np

#Colors
WHITE   = 0xFFFFFFFF
BLACK   = 0xFF000000
RED     = 0xFF0000FF
GREEN   = 0xFF00FF00
BLUE    = 0xFFFF0000

MODES   = ["Draw", "Fill", "Eraser"]
BGCOLOR = [.7, .7, .7 , 1]
KEYBOARD = key.KeyStateHandler()

class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.color = BLACK
        self.brush_size = 0
        self.mode = MODES[0]
        #Initializing canvas
        canvas.x, canvas.y = self.width//2, self.height//2
        canvas.set_size(640, 480); canvas.data.fill(WHITE)
            
        #Initializing draw history module
        dhist.data[dhist.index] = np.copy(canvas.data)
        dhist.index = 0
        
        self.push_handlers(KEYBOARD)
        pyglet.clock.schedule_interval(self.update, 1/60)

    def save(self):
       save_img = canvas.data.tobytes()
       save_img = pyglet.image.ImageData(canvas.width, canvas.height, 'RGBA', save_img)

       save_img.save("Untitled.png")
       print("[Image saved as \"Untitled.png\" in current directory]")

    def zoom(self, x, y, scroll_y):
        
        #Recording old dimensions and modifying zoom
        old_width, old_height = canvas.width*canvas.zoom, canvas.height*canvas.zoom
        canvas.zoom = min(max(canvas.zoom+scroll_y/10, canvas.min_zoom), canvas.max_zoom)
        
        #Moving canvas
        new_width, new_height = canvas.width*canvas.zoom, canvas.height*canvas.zoom
        per_width, per_height = new_width/old_width, new_height/old_height #Percentage
        delta_x, delta_y      = (x-canvas.x)*per_width, (y-canvas.y)*per_height
        canvas.x, canvas.y    = x-delta_x, y-delta_y

    def set_color(self, color):
        self.color = color

        print("Color set to: ", end="")
        if color == BLACK: print("Black")
        if color == WHITE: print("White")
        if color == RED: print("Red")
        if color == GREEN: print("Green")
        if color == BLUE: print("Blue")

    def set_thickness(self, size):
        self.brush_size = min(max(0, size), 50)
        print("Brush size is now: %d"%(self.brush_size))

    def flood_fill(self, x, y): 
        #start = time.perf_counter()
        clib.flood_fill(self.color, x, y)
        dhist.update()
        #end = time.perf_counter()
        #print("Filled in %.5f seconds"%(end-start))

    def draw(self, x, y, mx, my): 
        color = self.color
        if self.mode == MODES[2]: color = WHITE
        clib.draw(color, self.brush_size, x, y, mx, my)

    def tool_mode(self, mode):
        print("Set mode: "+MODES[mode])
        self.mode = MODES[mode]

    def on_key_press(self, symbol, mod):
        """
        This function will hold the special keys for
        changing tool mode(i.e: 1 = Pencil, 2 = Bucket).
        """
        if mod & key.MOD_CTRL:
            if symbol == key.S: self.save()
            if symbol == key.Z: dhist.undo()
            if symbol == key.Y: dhist.redo()

            if symbol == key._1: self.set_color(BLACK)
            if symbol == key._2: self.set_color(WHITE)
            if symbol == key._3: self.set_color(RED)
            if symbol == key._4: self.set_color(GREEN)
            if symbol == key._5: self.set_color(BLUE)

        if symbol == key.B: self.tool_mode(0)
        if symbol == key.F: self.tool_mode(1)
        if symbol == key.C: canvas.data.fill(WHITE); dhist.update()
        if symbol == key.E: self.tool_mode(2)
        if symbol == key.R:
            canvas.zoom = 1
            canvas.x = self.width//2
            canvas.y = self.height//2

    def on_mouse_press(self, x, y, bttn, mod): 

        #Fill Mode functions
        if self.mode == MODES[1]: 
            if bttn == 1: self.flood_fill(x, y)

        mouse.x, mouse.y = x, y

    def on_mouse_release(self, x, y, bttn, mod):
        if self.mode == MODES[0] or self.mode == MODES[2]: dhist.update()

    def on_mouse_drag(self, x, y, dx, dy, bttn, mod):
        
        if (self.mode == MODES[0] or self.mode == MODES[2]) and bttn == 1:
            self.draw(x, y, mouse.x, mouse.y)

        if bttn == 2: canvas.x += dx; canvas.y += dy
        mouse.x, mouse.y = x, y

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not KEYBOARD[key.LSHIFT]: self.zoom(x, y, scroll_y)
        else:
            if scroll_y > 0: self.set_thickness(self.brush_size + 1)
            else: self.set_thickness(self.brush_size - 1)

    def on_draw(self):
        output = canvas.data.tobytes()
        output = pyglet.image.ImageData(canvas.width, canvas.height, 'RGBA', output)
        output = output.get_texture()

        glClearColor(*BGCOLOR)

        if canvas.zoom > 1:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
        self.clear()
        output.width = int(canvas.width*canvas.zoom)
        output.height = int(canvas.height*canvas.zoom)
        output.anchor_x = output.width//2
        output.anchor_y = output.height//2
        output.blit(canvas.x, canvas.y)

        gui.draw()

    def update(self, dt):
        gui.update()
