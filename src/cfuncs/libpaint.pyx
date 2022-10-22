import numpy as np
from src.core import*

cimport numpy as np
from cfuncs.libpaint cimport*

from libc.stdio cimport printf
from libc.stdint cimport uint32_t
from libc.stdlib cimport free

#C functions for pointer initialization
cdef _flood_fill(np.uint32_t[:] data, uint32_t n_color, uint32_t color, int x, int y):
    cdef uint32_t *dpointer = &data[0]
    floodFill(dpointer, n_color, color, x, y)

cdef _draw(np.uint32_t[:] data, int radius, int x, int y, int mx, int my, uint32_t color):
    cdef uint32_t *dpointer = &data[0]
    draw(dpointer, radius, x, y, mx, my, color)

#Python section
def set_size(int w, int h):
    resize(w, h)
    
def rel_pos(int x, int y):
    rel_x = (x-canvas.x+canvas.width//2*canvas.zoom)/canvas.zoom
    rel_y = (y-canvas.y+canvas.height//2*canvas.zoom)/canvas.zoom
    return int(rel_x), int(rel_y)

def flood_fill(uint32_t new_color, int x, int y):
    x, y = rel_pos(x, y)
    if width != canvas.width or height != canvas.height: resize(canvas.width, canvas.height)
    if not in_borders(x, y): return
    
    cdef uint32_t old_color = np.copy(canvas.data[y*canvas.width+x]) 
    if old_color == new_color: return

    _flood_fill(canvas.data, new_color, old_color, x, y)

#Called drawp to no interfer with "draw" function from C script
def drawp(uint32_t new_color, int radius, int x, int y, int mx, int my):
    x, y = rel_pos(x, y); mx, my = rel_pos(mx, my)
    if width != canvas.width or height != canvas.height: resize(canvas.width, canvas.height)
    _draw(canvas.data, radius, x, y, mx, my, new_color)
