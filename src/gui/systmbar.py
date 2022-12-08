import pyglet
import pyglet.gui as gui
from tkinter import filedialog

import src.core.mouse as mouse
import res.systmicons as sicons

#Temporary buttong background until I make something
def solid_image(color, w, h):
	image = pyglet.image.SolidColorImagePattern(color)
	return image.create_image(w, h)

def press_savedisk():
    import src.windows as wins
    wins.ask_save_window()
    savedisk_button._sprite.image = savedisk_button._depressed_img
   

#Colors
DEPRESSED = solid_image((175,175,175,255), 32, 32)
PRESSED = solid_image((125,125,125,255), 32, 32)
HOVER = solid_image((150,150,150,255), 32, 32)

#Groups and batch
BACKGROUND = pyglet.graphics.OrderedGroup(0)
FOREGROUND = pyglet.graphics.OrderedGroup(1)
#BACKGROUND = pyglet.graphics.Group(0)
#FOREGROUND = pyglet.graphics.Group(1)
BATCH = pyglet.graphics.Batch()

#Sprites
savedisk_sprite = pyglet.sprite.Sprite(sicons.SAVEDK, group=FOREGROUND, batch=BATCH)

savedisk_button = gui.PushButton(0, 0, pressed=PRESSED, depressed=DEPRESSED, hover=HOVER, group=BACKGROUND, batch=BATCH)

savedisk_button.set_handler('on_press', press_savedisk)


def set_frame(frame):
    frame.add_widget(savedisk_button)

def draw():
	BATCH.draw()

def update():
	pass
