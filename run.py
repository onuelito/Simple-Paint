import pyglet
import pyglet.gui as gui
from pyglet.window import key

from src.core import*
import src.windows as wins
import src.gui as local_gui

#Creating frames
TOOLS_FRAME = gui.Frame(window, order=0)
SYSTM_FRAME = gui.Frame(window, order=1)

local_gui.set_frame(TOOLS_FRAME, SYSTM_FRAME)

def on_draw():
	local_gui.draw()

def update(dt):
	local_gui.update()


def on_key_press(symbol, mod):

    if mod & key.MOD_CTRL:
        if symbol == key.S: wins.ask_save_window()

def on_close():
    window.close()

window.on_draw = on_draw
window.on_close = on_close
window.on_key_press = on_key_press
pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
