import pyglet
import pyglet.gui as gui

from src.core import*
import src.gui as local_gui

#Creating frames
MAIN_FRAME = gui.Frame(window)
local_gui.set_frame(MAIN_FRAME)

def on_draw():
	local_gui.draw()
	
def update(dt):
	local_gui.update()

window.on_draw = on_draw
pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
