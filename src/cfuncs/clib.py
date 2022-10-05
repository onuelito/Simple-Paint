"""
Module containing every C functions related
to paint.
"""

import numpy as np
from ctypes import*
from src.core import*

#Initializing and linking c_utils//
PATH = "./c_utils/libpaint.so"

libpaint = CDLL(PATH)
libpaint.in_borders.restype = c_bool
libpaint.resize.argtypes = [c_int, c_int]
libpaint.in_borders.argtypes = [c_int, c_int]
libpaint.floodFill.argtypes = [POINTER(c_uint32), c_uint32, c_uint32, c_int, c_int]
libpaint.draw.argtypes = [POINTER(c_uint32), c_int, c_int, c_int, c_int, c_int, c_uint32]

width, height = 0, 0 #Dimensions update

#Function used when resizing canvas
def resize():
    global width, height
    width = canvas.width
    height= canvas.height

    libpaint.resize(width, height)

#Transformation function to get the x & y relative to canvas
def rel_pos(x, y):
	rel_x = (x-canvas.x+canvas.width//2*canvas.zoom)/canvas.zoom
	rel_y = (y-canvas.y+canvas.height//2*canvas.zoom)/canvas.zoom
	return int(rel_x), int(rel_y)

def in_borders(x, y)->bool: return libpaint.in_borders(x, y)

def draw(color, thickness, x, y, mx, my):
    x, y = rel_pos(x, y); mx, my = rel_pos(mx, my) #Relative position

    if width != canvas.width or height != canvas.height: resize()
    dpointer = canvas.data.ctypes.data_as(POINTER(c_uint32))
    libpaint.draw(dpointer, thickness, x, y, mx, my, color)

def flood_fill(new_color, x, y):
    x, y = rel_pos(x, y) #Relative Position
    if width != canvas.width or height != canvas.height: resize()
    if not in_borders(x, y): return
    old_color = np.copy(canvas.data[y*canvas.width+x])
    
    if old_color == new_color: return #Ignore if smae
    
    dpointer = canvas.data.ctypes.data_as(POINTER(c_uint32))
    libpaint.floodFill(dpointer, new_color, old_color, x, y)
