#!/usr/bin/env python
import pyglet
pyglet.options["debug_gl"] = False

import numpy as np
from pyglet.gl import*
from pyglet.window import key

from src import treeglet as tglet
from src import cfuncs
from src import core

"""
TASKS :

    Colors Selector Update:
        Hexadecimal TextEntry to set your own color


"""

#Loading paths
pyglet.resource.path.append("res/icons/app_icons")
pyglet.resource.add_font("res/fonts/Retro Gaming.ttf")

#Loading images
es_icon = pyglet.resource.image("eraser.png")
pn_icon = pyglet.resource.image("pencil.png")
bk_icon = pyglet.resource.image("bucket.png")
fp_icon = pyglet.resource.image("floppy.png")
fd_icon = pyglet.resource.image("folder.png")
pk_icon = pyglet.resource.image("picker.png")

#Button functions
def SolidColor(color, width, height):
    return pyglet.image.SolidColorImagePattern(color).create_image(width, height)

def SolidTextures(color, width, height):
    dimage = SolidColor(color[0:4], width, height)
    pimage = SolidColor(color[4:8], width, height)
    himage = SolidColor(color[8:16], width, height)

    return dimage, pimage, himage


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(self.width, self.height)

        self.batch = pyglet.graphics.Batch()
        self.group = pyglet.graphics.Group()
        self.toolTip = pyglet.text.Label(
            text="Tool: None",
            x=self.width-10,
            y=10,
            font_name="Retro Gaming",
            anchor_x="right",
        )

        self.setup_gui()
        self.windows = {
            "save": None,
            "open": None,
        }
        self.app_config = core.Config() #Can't name `config` cause pyglet window has it :/
        self.colorP = core.ColorPicker(self, self.width//2-50, self.height//2-50, diameter=100)
        self.colorP.visible = False

        self.hLabel = pyglet.text.HTMLLabel(
                text=self.app_config["HELP"], 
                x=self.width//2, 
                y=self.height//2, 
                multiline=True,
                anchor_x="center",
                anchor_y="center",
                width=350,)
                #batch=self.batch)
        self.hBackground = pyglet.shapes.Rectangle(
            self.width//2-200,
            self.height//2-150,
            400,
            340,
            color=(255,255,255),
        )
        self.hBackground.opacity = 125
        self.showHelp = False
        self.canvas = core.Canvas(self, self.width//2, self.height//2, 640, 480)

        #Handlers
        self.key = key
        self.nav = core.Navigator()
        self.key_manager  = key.KeyStateHandler()
        self.mouse_handler= tglet.MouseHandler()
        self.tool_manager = core.ToolManager(self)

        self.push_handlers(self.key_manager)
        self.push_handlers(self.mouse_handler)
        pyglet.clock.schedule_interval(self.nav.update, 1) #Might want to put that in initialized window for
        self.oFrame.mouse_handler = self.mouse_handler
        self.frame.mouse_handler = self.mouse_handler







    def setup_gui(self):

        #Creating the root frame
        self.frame = tglet.Frame(
            self, 
            0, 
            0, 
            self.width, 
            32, 
            group=self.group, 
            batch=self.batch
        )
        self.frame.z = 0
        self.frame.style(stretch_resolution=True, stretch_y=False, fixed_y=True)
        #self.frame.background_visible=False
        self.frame.background.image = SolidColor((178, 178, 178, 255), self.width, 32)
        
        self.push_handlers(self.frame)
        
        #Button setup
        bimages = SolidTextures((178,178,178,255,128,128,128,255,158,158,158,255), 32, 32)
        self.eraserB = tglet.IconToggleButton(es_icon, 0, 0, *bimages, anchor_x="center",)
        self.pencilB = tglet.IconToggleButton(pn_icon, 0, 0, *bimages, anchor_x="center",)
        self.bucketB = tglet.IconToggleButton(bk_icon, 0, 0, *bimages, anchor_x="center",)
        self.pickerB = tglet.IconToggleButton(pk_icon, 0, 0, *bimages, anchor_x="center",)
        self.floppyB = tglet.IconButton(fp_icon, 0, 0, *bimages)
        self.folderB = tglet.IconButton(fd_icon, 0, 0, *bimages)

        self.frame.add_widget(self.pencilB, x=self.frame.width//2-96, y=0)
        self.frame.add_widget(self.bucketB, x=self.frame.width//2-32, y=0)
        self.frame.add_widget(self.eraserB, x=self.frame.width//2+32, y=0)
        self.frame.add_widget(self.pickerB, x=self.frame.width//2+96, y=0)

        #Attaching events

        @self.eraserB.event
        def on_toggle(value):
            if value == False: self.tool_manager.notool(); return
            self.pencilB.pressed = False
            self.bucketB.pressed = False
            self.pickerB.pressed = False

            self.tool_manager.tool = core.TOOL_ID.ERASER

        @self.pencilB.event
        def on_toggle(value):
            if value == False: self.tool_manager.notool(); return
            self.eraserB.pressed = False
            self.bucketB.pressed = False
            self.pickerB.pressed = False

            self.tool_manager.tool = core.TOOL_ID.PENCIL

        @self.bucketB.event
        def on_toggle(value):
            if value == False: self.tool_manager.notool(); return
            self.pencilB.pressed = False
            self.eraserB.pressed = False
            self.pickerB.pressed = False

            self.tool_manager.tool = core.TOOL_ID.BUCKET

        @self.pickerB.event
        def on_toggle(value):
            if value == False: self.tool_manager.notool(); return
            self.pencilB.pressed = False
            self.eraserB.pressed = False
            self.bucketB.pressed = False

            self.tool_manager.tool = core.TOOL_ID.PICKER

        @self.floppyB.event
        def on_click():
            self.save_window()

        @self.folderB.event
        def on_click():
            self.open_window()


        self.oFrame = tglet.Frame(
            self,
            0,
            0,
            32,
            self.height,
            batch=self.batch
        )
        self.oFrame.z = 1
        self.oFrame.background.image = SolidColor((178, 178, 178, 255), 32, self.height)

        self.oFrame.add_widget(self.floppyB, x=0, y=0)
        self.oFrame.add_widget(self.folderB, x=0, y=32)


    def compress(self):
        import os

        #content = self.canvas.data.tobytes()
        #with open(os.getcwd()+"/data", "w") as f:
        #    f.write(self.canvas.data)
        #self.canvas.data.save("data")
        np.save("data", self.canvas.data*30)
        print("Data written")

    def read(self):
        return
        import os

        with open(os.getcwd()+"/Untitled.png", "rb") as f:
            print(f.read())
            #data = np.frombuffer(f.read(), dtype="uint32")
        #self.canvas.data = np.copy(data)
        #self.canvas.refresh()
        #print("File loaded", data)

    def save_window(self):
        if self.windows["save"] != None:
            print("Save Window Already Exists!")
            return
        self.windows["save"] = core.SaveWindow(
            self,
            width=640,
            height=480,
            caption="Save image as...",
            resizable=True,
        )

        #self.windows["save"].switch_to()

    def open_window(self):
        if self.windows["open"] != None:
            print("Open Window Already Exists!")
            return
        self.windows["open"] = core.OpenWindow(
            self,
            width=640,
            height=480,
            caption="Open Image",
            resizable=True,
        )

    """
    Event Management
    """
    def on_key_press(self, symbol, modifiers):
        if symbol == key.R: self.canvas.reset()
        if symbol == key.B:
            self.pencilB.on_mouse_press(*self.pencilB.center, 0, 0)
            self.pencilB.on_mouse_motion(*self.pencilB.bottom_left, 0, 0)

        if symbol == key.F:
            self.bucketB.on_mouse_press(*self.bucketB.center, 0, 0)
            self.bucketB.on_mouse_motion(*self.bucketB.bottom_left, 0, 0)

        if symbol == key.E:
            self.eraserB.on_mouse_press(*self.eraserB.center, 0, 0)
            self.eraserB.on_mouse_motion(*self.eraserB.bottom_left, 0, 0)

        if symbol == key.P:
            self.pickerB.on_mouse_press(*self.pickerB.center, 0, 0)

        if symbol == key.S and self.key_manager[key.LCTRL]:
            self.save_window()

        if symbol == key.O and self.key_manager[key.LCTRL]:
            self.open_window()

        if symbol == key.Z and self.key_manager[key.LCTRL]:
            if self.key_manager[key.LSHIFT]: self.canvas.redo()
            else: self.canvas.undo()

        if symbol == key.H: self.showHelp = not self.showHelp

        if symbol == key.TAB:
            self.compress()

        if symbol == key.R:
            self.read()

        if symbol == key.C: 
            self.canvas.clear()
            self.canvas._update()

        if symbol == key.V: self.colorP.visible = not self.colorP.visible


    def on_mouse_press(self, x, y, button, modifiers):
        self.oFrame.on_mouse_press(x, y, button, modifiers)

        self.colorP.on_mouse_press(x, y, button, modifiers)
        self.tool_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.oFrame.on_mouse_release(x, y, button, modifiers)

        self.tool_manager.on_mouse_release(x, y, button, modifiers)
        self.colorP.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.oFrame.on_mouse_motion(x, y, dx, dy)

        self.tool_manager.on_mouse_motion(x, y, dx, dy)
        if self.key_manager[key.LALT]: 
            self.canvas.x += dx
            self.canvas.y += dy 


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.oFrame.on_mouse_drag(x, y, dx, dy, button, modifiers)

        self.colorP.on_mouse_drag(x, y, dx, dy, button, modifiers)
        self.tool_manager.on_mouse_drag(x, y, dx, dy, button, modifiers)

        if button ==2: self.canvas.x += dx; self.canvas.y += dy 

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.tool_manager.on_mouse_scroll(x, y, scroll_x, scroll_y)
        if self.key_manager[key.LCTRL]: self.canvas._zoom(x, y, scroll_y); return

    def on_draw(self):
        glClearColor(0.7, 0.7, 0.7, 1.0)
        self.clear()

        if self.canvas.zoom >= 1:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self.hLabel.x = self.width//2
        self.hLabel.y = self.height//2
        self.hBackground.x = self.width//2 - self.hBackground.width//2
        self.hBackground.y = self.height//2 - self.hBackground.height//2

        self.colorP.x = self.width//2 - self.colorP.diameter//2-25
        self.colorP.y = self.height//2 - self.colorP.diameter//2-25

        self.canvas.draw()
        self.batch.draw()
        self.colorP.draw()
        #vertices.draw(GL_QUADS)
        if self.showHelp: self.hBackground.draw(); self.hLabel.draw()
        self.toolTip.draw()
        self.toolTip.x = self.width-10


    def on_file_drops(self, x, y, paths):
        pass

    def on_file_drop(self, x, y, path):
        pass

    def on_close(self):
        for name, value in self.windows.items():
            if value != None: value.on_close()
        self.close()

window = Window(800, 600, caption="Simple-Paint: New File", resizable=True)

pyglet.app.run()
