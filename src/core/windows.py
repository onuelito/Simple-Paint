"""
Application additionnal windows for file management
"""

import os
import pyglet
from pyglet.gl import*

import src.treeglet as tglet

def SolidColor(color, w, h):
    return pyglet.image.SolidColorImagePattern(color).create_image(w, h)

class WindowBase(pyglet.window.Window):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.content = set()
        self.batch= pyglet.graphics.Batch()


        self._init_frame()
        self._init_widgets()

    def _init_frame(self):
        pass

    def __init__widgets(self):
        pass


    def on_content_change(directories, files):
        """
        Function in response to navigator changing content
        """


class SaveWindow(WindowBase):
    def __init__(self, root, *args, **kwargs):

        self.mouse_handler = tglet.MouseHandler()
        self.push_handlers(self.mouse_handler)

        super().__init__(root, *args, **kwargs)

        self.root.nav.set_handler("on_content_change", self.on_content_change)
        self.warnLabel = pyglet.text.Label(
            "[Warning] File already exists! It will be overwritten.",
            x = 10,
            y = self.height - 60,
            anchor_y ="bottom",
            font_name="Retro Gaming",
            color=(255,255,0,255),
            font_size=8,
        )
        self.set_minimum_size(320, 240)

    """
    Window functions
    """
    def _init_frame(self):


        self.frames = {
            "Shortcut"  : tglet.Frame(self, 0, 25, 150, 375, batch=self.batch),
            "Files"     : tglet.ScrollFrame(self, 148, 25, self.width-150+2, 375, batch=self.batch),
            "Top"       : tglet.Frame(self, 0, self.height, self.width, self.height-25-375, anchor_y="top", batch=self.batch),
            "Bottom"    : tglet.Frame(self, 0, 0, self.width, 25, batch=self.batch)
        }

        self.frames["Shortcut"].background.image = SolidColor((120,120,120,255), 150, 375)
        self.frames["Shortcut"].style(stretch_resolution=True, sticky_y=False, stretch_x=False)

        self.frames["Files"].style(stretch_resolution=True, sticky_y=False, sticky_x=False)
        self.frames["Files"].min_scroll_y=0
        self.frames["Files"].scroll_y_multiplier = -10

        self.frames["Bottom"].style(stretch_resolution=True, sticky_y=False, stick_x=False, stretch_y=False)
        self.frames["Bottom"].background_visible = False

        self.frames["Top"].background.image = SolidColor((155,155,155,255), self.width, self.height-25-375)
        self.frames["Top"].style(stretch_resolution=True, stretch_y=False)


        #Handlers
        for _,frame in self.frames.items(): frame.mouse_handler=self.mouse_handler; self.push_handlers(frame)

    def _init_widgets(self):
        es_icon = pyglet.resource.image("pencil.png")

        self.homeButton = tglet.TextButton(
            "HOME",
            0,
            0,
            SolidColor((150,150,150,255), self.frames["Shortcut"].width, 75),
            SolidColor((100,100,100,255), self.frames["Shortcut"].width, 75),
            SolidColor((125,125,125,255), self.frames["Shortcut"].width, 75),

            anchor_x="center",
            anchor_y="top"
        )

        self.homeButton.style_text(
            #color=(125,125,125,255), 
            anchor_x="center", 
            anchor_y="center",
            font_name="Retro Gaming")
        self.homeButton.text_x = "50%"; self.homeButton.text_y="50%"

        self.deskButton = tglet.TextButton(
            "DESKTOP",
            0, 
            0, 
            SolidColor((150,150,150,255), self.frames["Shortcut"].width, 75),
            SolidColor((100,100,100,255), self.frames["Shortcut"].width, 75),
            SolidColor((125,125,125,255), self.frames["Shortcut"].width, 75),

            anchor_x="center",
            anchor_y="top",
        )

        self.deskButton.style_text(
            #color=(125,125,125,255), 
            anchor_x="center", 
            anchor_y="center",
            font_name="Retro Gaming")
        self.deskButton.text_x = "50%"; self.deskButton.text_y="50%"

        self.docButton = tglet.TextButton(
            "DOCUMENTS",
            0, 
            0, 
            SolidColor((150,150,150,255), self.frames["Shortcut"].width, 75),
            SolidColor((100,100,100,255), self.frames["Shortcut"].width, 75),
            SolidColor((125,125,125,255), self.frames["Shortcut"].width, 75),
            anchor_x="center",
            anchor_y="top",
        )
        self.docButton.style_text(
            #color=(125,125,125,255), 
            anchor_x="center", 
            anchor_y="center",
            font_name="Retro Gaming")
        self.docButton.text_x = "50%"; self.docButton.text_y="50%"

        #Attaching Events
        @self.homeButton.event
        def on_click():
            self.root.nav.chdir(os.path.expanduser("~"))

        @self.deskButton.event
        def on_click():
            self.root.nav.chdir(os.path.expanduser("~/Desktop"))

        @self.docButton.event
        def on_click():
            self.root.nav.chdir(os.path.expanduser("~/Documents"))


        #self.frames["Files"].add_widget(self.fEntry, x=10, y=40)
        self.frames["Shortcut"].add_widget(
            self.homeButton, 
            x=self.frames["Shortcut"].width//2, 
            y=self.frames["Shortcut"].height
        )

        self.frames["Shortcut"].add_widget(
            self.deskButton, 
            x=self.frames["Shortcut"].width//2, 
            y=self.frames["Shortcut"].height-75
        )

        self.frames["Shortcut"].add_widget(
            self.docButton,
            x=self.frames["Shortcut"].width//2, 
            y=self.frames["Shortcut"].height-75*2
        )


        """
        Top Frame
        """
        save_name = self.root.app_config["MANAGER"]["SAVE_NAME"] or "Untitled.png"
        self.fileEntry = tglet.TextEntry(
            save_name,
            0,
            0,
            SolidColor((105,105,105,255), 500, 30),
            caret_color=(255,255,255),
        )
        self.fileEntry.illegal_characters = "<>:\"\\/|?*" #Silly Windows Users


        self.saveButton = tglet.TextButton(
            "Save",
            0,
            0,
            SolidColor((100, 100, 100, 255), 100, 30),
            SolidColor((50, 50, 50, 255), 100, 30),
            SolidColor((75, 75, 75, 255), 100, 30),
            anchor_x = "right",
        )

        @self.saveButton.event
        def on_click():
        
            #Silly Windows Users
            check = 0
            for c in self.fileEntry._document.text:
                if check == 0:
                    if c == " ": continue
                    if c.lower() == "c": check += 1
                    else: break
                if check == 1:
                    if c.lower() == "o": check += 2
                    else: break
                if check == 2:
                    if c.lower() == "n": check += 3; break
                    else: break
                
            if check == 3: print("You think you're slick? You can't do that"); return
        
            feedback = self.root.canvas.save_as(self.fileEntry._document.text)
            if feedback: self.on_close()
        self.saveButton.style(sticky_x=True)

        self.fileEntry.style(stretch_resolution=True, fill_x=True, sticky_x=False, stretch_y=False)
        self.frames["Top"].add_widget(self.fileEntry, x=10, y=40, z=0)
        self.frames["Top"].add_widget(self.saveButton, x=self.frames["Top"].width-10, y=40, z=1)
        self.saveButton.style_text(font_name="Retro Gaming", anchor_x="center", anchor_y="center")
        self.saveButton.text_x="50%"; self.saveButton.text_y="50%"
        self.fileEntry.style_document(dict(font_name="Retro Gaming", color=(255,255,255,255)))
        self.fileEntry.layout_x = 10
        self.fileEntry.layout_y = -3

        """
        Bottom
        """
        self.climbButton = tglet.TextButton(
            "CLIMB",
            0,
            0,
            SolidColor((150, 150,150,255), 125, 25),
            SolidColor((100, 100,100,255), 125, 25),
            SolidColor((125, 125,125,255), 125, 25),
            anchor_x="right",
        )

        @self.climbButton.event
        def on_click():
            self.root.nav.chdir(self.root.nav.climbdir(self.root.nav.cwd))
            self.root.nav.update(0)


        self.climbButton.style_text(font_name="Retro Gaming", anchor_x="center", anchor_y="center")
        self.climbButton.text_x="50%"; self.climbButton.text_y = "50%"
        self.frames["Bottom"].add_widget(self.climbButton, x=self.frames["Bottom"].width, y=0)

        """
        Files
        """
        for i in range(0, 100):
            button = tglet.TextButton(
                "[File Type] Template",
                0,
                0,
                SolidColor((150,150,150,255),self.frames["Files"].width+1, 30), #Adding +1 to correct imperfection
                SolidColor((100,100,100,255), self.frames["Files"].width+1, 30),
                SolidColor((125,125,125,255), self.frames["Files"].width+1, 30),
                anchor_y="top",
            )
            button.style_text(font_name="Retro Gaming", anchor_y="center")
            button.text_y="50%"; button.text_x = 10
            button.style(stretch_resolution=True, stretch_y=False)

            self.frames["Files"].add_widget(
                button,
                x=-0.1, #Imperfection correction
                y=self.frames["Files"].height-i*30,
            )
            button.visible = False
    
        self.pathLabel = pyglet.text.Label(
            text=self.root.nav.cwd,
            x=5,
            y=8,
            font_name="Retro Gaming",
            font_size=8,
            color=(70,70,70,255),
            batch=self.batch
        )
        self._update_content()

    def _update_content(self):

        def set_directory(widget, path):
            def click():
                self.root.nav.chdir(path)
            widget.on_click = click

        def set_file(widget, name):
            def click():
                self.fileEntry._document.text = name
                #if name[-4:].lower() == ".png":
                #    self.fileEntry._document.text = name

            widget.on_click=click

        for i, name in enumerate(self.root.nav.dirts):
            button = self.frames["Files"].widgets[i]
            button.style_text(text="[DIRECTORY] "+name)
            button.visible = True
            
            set_directory(button, name)
            self.content.add(button)

        for i, name in enumerate(self.root.nav.files):
            button = self.frames["Files"].widgets[i+len(self.root.nav.dirts)]
            button.style_text(text="[FILE] "+name)
            button.visible = True
            set_file(button, name)
            self.content.add(button)

    """
    Default Events
    """
    
    def on_content_change(self, directories, files):
        for button in self.content:
            button.on_click = lambda: None
            button.visible = False

        self.content = set()
        self._update_content()
        self.pathLabel.text = self.root.nav.cwd
        self.frames["Files"].scroll_y = 0

    def on_key_press(self, symbol, modifiers):
        if symbol == self.root.key.ESCAPE and self.mouse_handler.ctentry == None: 
            self.climbButton.dispatch_event("on_click")

    def on_draw(self):
        glClearColor(0.7, 0.7, 0.7, 1.0)
        self.clear()
        self.batch.draw()

        if self.fileEntry._document.text in self.root.nav.files:
            self.warnLabel.y = self.height-60
            self.warnLabel.draw()

    def on_close(self):

        for _,frame in self.frames.items():
            if frame: self.remove_handlers(frame)
        self.root.windows["save"] = None
        self.close()

class OpenWindow(SaveWindow):
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        """
        Customizing
        """
        self.saveButton.style_text(text = "Open")
        @self.saveButton.event
        def on_click():
            image = self.root.canvas.open(self.fileEntry._document.text)
            if image: self.on_close()

    def on_draw(self):
        glClearColor(0.7, 0.7, 0.7, 1.0)
        self.clear()
        self.batch.draw()
        """
        if self.fileEntry._document.text in self.root.nav.files:
            self.warnLabel.y = self.height-60
            self.warnLabel.draw()
        """

    def on_close(self):
        for _,frame in self.frames.items():
            if frame: self.remove_handlers(frame)

        self.root.windows["open"] = None
        self.close()
