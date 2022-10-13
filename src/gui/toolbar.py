import pyglet
import pyglet.gui as gui

import src.core.mouse as mouse
import res.toolicons as ticons
import src.tools.ids as toolID

#Temporary buttong background until I make something
def solid_image(color, w, h):
	image = pyglet.image.SolidColorImagePattern(color)
	return image.create_image(w, h)

#Tool switching functions
def toggle_pencil(value):
	if value: mouse.set_toolmode(toolID.PENCIL)
	else: mouse.set_toolmode(toolID.NOTOOL)

def toggle_bucket(value):
	if value: mouse.set_toolmode(toolID.BUCKET)
	else: mouse.set_toolmode(toolID.NOTOOL)

def toggle_eraser(value):
	if value: mouse.set_toolmode(toolID.ERASER)
	else: mouse.set_toolmode(toolID.NOTOOL)

	
#Colors
DEPRESSED = solid_image((175,175,175,255), 32, 32)
PRESSED = solid_image((125,125,125,255), 32, 32)
HOVER = solid_image((150,150,150,255), 32, 32)

#Groups and batch
BACKGROUND = pyglet.graphics.OrderedGroup(0)
FOREGROUND = pyglet.graphics.OrderedGroup(1)
BATCH = pyglet.graphics.Batch()

#Creating Sprites
pencil_sprite = pyglet.sprite.Sprite(ticons.PENCIL ,group=FOREGROUND, batch=BATCH)
eraser_sprite = pyglet.sprite.Sprite(ticons.ERASER, group=FOREGROUND, batch=BATCH)
bucket_sprite = pyglet.sprite.Sprite(ticons.BUCKET, group=FOREGROUND, batch=BATCH)
#colors_sprite = pyglet.sprite.Sprite(ticons.COLORS, group=FOREGROUND, batch=BATCH) #Work in progress


iconbg = pyglet.sprite.Sprite(solid_image((175,175,175,255), 150, 32), x=320)#Tempoarary background
pencil_button = gui.ToggleButton(iconbg.x, 0, pressed=PRESSED, depressed=DEPRESSED, hover=HOVER, group=BACKGROUND, batch=BATCH)
eraser_button = gui.ToggleButton(iconbg.x+62, 0, pressed=PRESSED, depressed=DEPRESSED, hover=HOVER, group=BACKGROUND, batch=BATCH)
bucket_button = gui.ToggleButton(iconbg.x+128, 0, pressed=PRESSED, depressed=DEPRESSED, hover=HOVER, group=BACKGROUND, batch=BATCH)

#Linking functions to their buttons
pencil_button.set_handler('on_toggle', toggle_pencil)
bucket_button.set_handler('on_toggle', toggle_bucket)
eraser_button.set_handler('on_toggle', toggle_eraser)

def set_frame(frame):
	frame.add_widget(pencil_button)
	frame.add_widget(eraser_button)
	frame.add_widget(bucket_button)

def draw(): 
	#Positioning sprite icons
	pencil_sprite.x = pencil_button.x; pencil_sprite.y = pencil_button.y
	eraser_sprite.x = eraser_button.x; eraser_sprite.y = eraser_button.y
	bucket_sprite.x = bucket_button.x; bucket_sprite.y = bucket_button.y
	
	iconbg.draw(); BATCH.draw()

def update():
	if mouse.x >= iconbg.x and mouse.x < iconbg.x+iconbg.width and mouse.y >= iconbg.y and mouse.y < iconbg.y+iconbg.height:
		mouse.target_gui = "toolbar"
	else:
		if mouse.target_gui == "toolbar": mouse.target_gui = None
