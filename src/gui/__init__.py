
import pyglet

import src.gui.toolbar as tbar
import src.core.mouse as mouse
import src.gui.systmbar as sbar


def set_frame(toolsframe, systmframe):
    tbar.set_frame(toolsframe)
    sbar.set_frame(systmframe)

def draw():
    tbar.draw()
    sbar.draw() 

def update():
    tbar.update()
    sbar.update()
