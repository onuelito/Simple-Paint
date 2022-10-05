import numpy as np
from ctypes import*

#Initial values
x, y = 0, 0
width, height, data = 0, 0, None
zoom, min_zoom, max_zoom = 1, 0.5, 5

def set_size(w, h):
    global width, height, data
    
    width   = w
    height  = h
    data    = np.zeros(dtype='uint32', shape=(width*height,))

