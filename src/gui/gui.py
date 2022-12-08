import pyglet
from pyglet.gl import*

from src.core.window import save as winsave
import src.windows.manager as man

class CustomFrame(pyglet.gui.Frame):
    enabled = True

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled: return
        """Pass the event to any widgets within range of the mouse"""
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_press(x, y, buttons, modifiers)
            self._active_widgets.add(widget)

    def on_mouse_release(self, x, y, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        if not self.enabled: return
        for widget in self._active_widgets:
            widget.on_mouse_release(x, y, buttons, modifiers)
        self._active_widgets.clear()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Pass the event to any widgets that are currently active"""
        if not self.enabled: return
        for widget in self._active_widgets:
            widget.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        self._mouse_pos = x, y

    def on_mouse_scroll(self, x, y, index, direction):
        """Pass the event to any widgets within range of the mouse"""
        if not self.enabled: return
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_scroll(x, y, index, direction)

    def on_mouse_motion(self, x, y, dx, dy):
        """Pass the event to any widgets within range of the mouse"""
        if not self.enabled: return
        for widget in self._active_widgets:
            widget.on_mouse_motion(x, y, dx, dy)
        for widget in self._cells.get(self._hash(x, y), set()):
            widget.on_mouse_motion(x, y, dx, dy)
            self._active_widgets.add(widget)
        self._mouse_pos = x, y

    def on_text(self, text):
        """Pass the event to any widgets within range of the mouse"""
        if not self.enabled: return
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text(text)

    def on_text_motion(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        if not self.enabled: return
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        """Pass the event to any widgets within range of the mouse"""
        if not self.enabled: return
        for widget in self._cells.get(self._hash(*self._mouse_pos), set()):
            widget.on_text_motion_select(motion)


class TextEntry(pyglet.gui.TextEntry):
    """
    Custom entry class for compatibility with application
    """
    illegal_characters = []
    def on_text(self, text):
        if not self.enabled:
            return
        if self._focus:
            if text in ('\r', '\n'):
                self.dispatch_event('on_commit', self._layout.document.text)
                self._set_focus(False)
                return
            if text in self.illegal_characters: return
            self._caret.on_text(text)

    def on_mouse_motion(self, x, y, dx, dy):
        return

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled:
            return

        if self._check_hit(x, y):
            self._set_focus(True)
            self._caret.on_mouse_press(x, y, buttons, modifiers)
        else:
            self.dispatch_event('on_commit', self._layout.document.text)
            self._set_focus(False)
            return

class TextButton(pyglet.gui.PushButton):
    def __init__(self, text, x, y, pressed, depressed, hover=None, batch=None, group=None):

        bg_group = pyglet.graphics.OrderedGroup(0, parent=group)
        fg_group = pyglet.graphics.OrderedGroup(1, parent=group)
        super().__init__(x, y, pressed, depressed, hover, batch, bg_group)

        self.list_group = None
        self.label = pyglet.text.Label(
            text,
            x=x+self._width//2,
            y=y+self._height//2,
            font_size=10,
            anchor_x="center",
            anchor_y="center",
            group=fg_group,
            batch=self._batch
        )

    def _check_hit(self, x, y):
        yOffset = 0
        sx = self._x
        sy = self._y
        sh = self._height
        sw = self._width
        if self.list_group:
            if not self.list_group.visible: return False
            if not self.list_group.check_hit(x, y): return False
            yOffset = self.list_group.offset_y

            #print(self.label.text, ":", sx+1, sy, "[Mouse]", x, y)

        return sx < x < sx + sw and sy < y - yOffset < sy + sh

    def style(self, **kwargs):
        for var, value in kwargs.items():
            setattr(self.label, var, value)


class ScissorGroup(pyglet.graphics.Group):
    def __init__(self, x, y, width, height, parent=None):

        super().__init__(parent)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.parent = parent

        self._offset_y = 0
        self.scrollable = False


    @property
    def offset_y(self): return self._offset_y

    @offset_y.setter
    def offset_y(self, value):
        if not self.scrollable: return
        self._offset_y = value

    def check_hit(self, x, y):
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height

    def set_state(self):
        """
        Copied from pyglet.text.layout.ScrollableTextLayout
        """
        glPushAttrib(GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_CURRENT_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_SCISSOR_TEST)
        glScissor(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )
        glTranslatef(0.0, self.offset_y, 0)

    def unset_state(self):
        glTranslatef(0.0, -self.offset_y, 0)
        glDisable(GL_SCISSOR_TEST)
        glPopAttrib()

class GuiList(pyglet.gui.WidgetBase):
    def __init__(self, x, y, width, height, group=None, batch=None):

        super().__init__(x, y, width, height)
        self._group = ScissorGroup(
            x,
            y,
            width,
            height,
            parent=group
        )
        self._batch = batch

        #Content variables
        self._content = list()
        bg_group = pyglet.graphics.OrderedGroup(0, parent=group)
        self._content_group = pyglet.graphics.OrderedGroup(1, parent=self._group)
        """
        self._background = pyglet.shapes.Rectangle(
            x,
            y,
            width,
            height,
            color=(75,75,75),
            group = bg_group,
            batch = batch
        )
        self._background.opacity = 150"""
        self._scrollable = self._group.scrollable

    @property
    def visible(self): return self._group.visible

    @property
    def scrollable(self): return self._scrollable

    @scrollable.setter
    def scrollable(self, value): 
        self._scrollable = value
        self._group.scrollable = value

    @property
    def content_group(self): return self._content_group

    @property
    def content_batch(self): return self._batch

    def hide(self): self._group.visible = False

    def show(self): self._group.visible = True

    def check_hit(self, x, y): return self._group.check_hit(x, y)

    def append(self, element): 
        element.list_group = self._group
        self._content.append(element)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        delta = scroll_y/(abs(scroll_y))
        self._group.offset_y -= delta*25
        self._group.offset_y = max(self._group.offset_y, 0)

class DropdownMenu(TextButton):
    def __init__(self, text, x, y, pressed, depressed, hover=None, batch=None, group=None):
        super().__init__(text, x, y, pressed, depressed, hover, batch, group)
        #self._list = GuiList(x, y, width, height, group=None, batch=None))
        self.lheight = 0
        self.cheight = 25
        self.batch = batch
        self._list = GuiList(x, y, self._width, 0, batch=batch)
        self._list.hide()

    def on_press(self): pass

    def show(self): pass

    def hide(self): pass

    def button_press(self): pass

    def add(self, name, frame):
        """
        Creating the button choice innit?
        """
        Prssd = Solid_Color(self._width, self.cheight, color=(100, 100, 100, 255))
        Dprsd = Solid_Color(self._width, self.cheight, color=(150, 150, 150, 255))
        Hover = Solid_Color(self._width, self.cheight, color=(125, 125, 125, 255))

        length = len(self._list._content)
        sgroup = self._list._group
        sgroup.height += self.cheight
        sgroup.y -= self.cheight

        button = TextButton(
            name,
            self._list.x,
            sgroup.y,
            Prssd,
            Dprsd,
            Hover,
            group=self._list.content_group,
            batch=self._list.content_batch
        )

        button.style(
            anchor_x="left",
            x = button.x + 4,
            font_size = 12
        )

        #@button.event
        #def on_press():
            #self.style(text=name)
            #self.hide()

        button.on_press = lambda: self.button_press(button)
        frame.add_widget(button)
        self._list.append(button)


def Solid_Color(width, height, color):
    return pyglet.image.SolidColorImagePattern(color).create_image(width, height)

def load_drop_down_menu(config):
    """
    Dropdown file extensions choices
    """
    TArea = config.area(config.TPercent)
    Width = int(TArea.width*0.75+4)

    Prssd = Solid_Color(Width, 25, color=(100, 100, 100, 255))
    Dprsd = Solid_Color(Width, 25, color=(150, 150, 150, 255))
    Hover = Solid_Color(Width, 25, color=(125, 125, 125, 255))


    dropdown = DropdownMenu(
        "Select file extension...",
        int(TArea.width*0.05-2),
        int(TArea.y+TArea.height*0.10),
        Prssd,
        Dprsd,
        Hover,
        batch=config.TBatch
    )

    @dropdown.event
    def on_press():
        if not dropdown._list.visible: dropdown.show()
        else: dropdown.hide()
    
    def show():
        dropdown._list.show()
        config.PFrame.enabled = False
        config.SFrame.enabled = False
        config.BFrame.enabled = False
        for button in config.SContent: button.enabled = False 
        for button in config.PathButton: button.enabled = False

    def hide():
        dropdown._list.hide()
        config.PFrame.enabled = True
        config.SFrame.enabled = True
        config.BFrame.enabled = True
        for button in config.SContent: button.enabled = True 
        for button in config.PathButton: button.enabled = True

    def button_press(button):
        dropdown.style(text=button.label.text)
        dropdown.hide()

        config.Extension = button.label.text

    dropdown.show = show
    dropdown.hide = hide
    dropdown.button_press = button_press

    dropdown.style(
        anchor_x = "left",
        x = dropdown.x + 4,
        font_size = 12,
    )

    dropdown.add(".png", config.TFrame)
    #Will be fixed up later on as no encoder
    #dropdown.add(".jpg", config.TFrame)
    #dropdown.add(".jpeg", config.TFrame)
    #dropdown.add(".bmp", config.TFrame)

    config.DropDownMn = dropdown
    config.TFrame.add_widget(dropdown)
    config.TFrame.add_widget(dropdown._list)

def load_directory(button, dirt):
    @button.event
    def on_press():
        man.chdir(dirt)
        print(button.label.text)
    button.label.text = "[Directory] "+ str(dirt)
    return button

def load_file(button, file):
    @button.event
    def on_press():
        pass
    button.label.text = "[File] "+str(file)
    return button

def detach_button(button):
    @button.event
    def on_press(): pass

def load_content(config):
    for button in config.PathButton:
        button.label.text = ""
        detach_button(button)
        button.enabled = False
        button._sprite.image = button._depressed_img
    config.PathButton.clear()

    index = 0
    for dirt in man.dirts:
        button = load_directory(config.PContent[index], dirt)
        config.PathButton.append(button)
        button.enabled = True
        index += 1
    for file in man.files: 
        button = load_file(config.PContent[index], file)
        config.PathButton.append(button)
        button.enabled = True
        index += 1

def preload_path_buttons(config):
    """
    Creating 100 buttons by default to prevent
    latency.
    """
    
    PHght = 25
    PArea = config.area(config.PPercent)
    Prssd = Solid_Color(int(PArea.width), PHght, color=(100, 100, 100, 255))
    Dprsd = Solid_Color(int(PArea.width), PHght, color=(150, 150, 150, 255))
    Hover = Solid_Color(int(PArea.width), PHght, color=(125, 125, 125, 255))

    config.Plist = GuiList(
        int(PArea.x),
        int(PArea.y),
        int(PArea.width),
        int(PArea.height),
        batch = config.PBatch
    )
    config.Plist.scrollable=True
    config.PFrame.add_widget(config.Plist)

    
    def button(index):
        pbutton = TextButton(
            "",
            int(PArea.x),
            int(PArea.y+PArea.height - PHght*(index+1)),
            Prssd,
            Dprsd,
            Hover,
            group=config.Plist.content_group,
            batch=config.Plist.content_batch
        )
        pbutton.style(
            anchor_x="left",
            x = pbutton.x+4
        )

        @pbutton.event
        def on_press():
            pass
       
        pbutton.enabled = False
        config.Plist.append(pbutton)
        config.window.push_handlers(pbutton)
        config.PContent.append(pbutton)

    for index in range(man.content_limit): button(index)

def load_shortcuts(config):
    """
    Shortcuts are the following directories:
     - Desktop
     - Documents
     - Pictures
     - Music
     - Downloads
    """
    import os

    SArea = config.area(config.SPercent)
    paths = [
        ["Desktop", os.path.expanduser("~/Desktop")],
        ["Documents", os.path.expanduser("~/Documents")],
        ["Pictures", os.path.expanduser("~/Pictures")],
        ["Music", os.path.expanduser("~/Music")],
        ["Downloads", os.path.expanduser("~/Downloads")],

    ]

    def button(text, path, x, y):
        button = TextButton(
            text,
            int(x),
            int(y),
            Prssd,
            Dprsd,
            Hover,
            batch=config.SBatch
        )
        @button.event
        def on_press():
            man.chdir(path)
        
        config.SContent.append(button)
        config.SFrame.add_widget(button)

    WIDTH, HEIGHT = int(SArea.width), 40
    Prssd = Solid_Color(WIDTH, HEIGHT, color=(100, 100, 100, 255))
    Dprsd = Solid_Color(WIDTH, HEIGHT, color=(150, 150, 150, 255))
    Hover = Solid_Color(WIDTH, HEIGHT, color=(125, 125, 125, 255))

    for i in range(0, len(paths)):
        y = SArea.y + SArea.height - (HEIGHT*(i+1))
        x = SArea.x
        button(paths[i][0], paths[i][1], x, y)

def load_bottom(config):
    WIDTH = 120
    BArea = config.area(config.BPercent)
    Prssd = Solid_Color(WIDTH, int(BArea.height), color=(100, 100, 100, 255))
    Dprsd = Solid_Color(WIDTH, int(BArea.height), color=(150, 150, 150, 255))
    Hover = Solid_Color(WIDTH, int(BArea.height), color=(125, 125, 125, 255))

    Climb = TextButton(
        "Climb",
        int(BArea.width-WIDTH),
        int(BArea.y),
        Prssd,
        Dprsd,
        Hover,
        batch=config.BBatch
    )

    group = ScissorGroup(
        int(BArea.x),
        int(BArea.y),
        int(BArea.width-WIDTH),
        int(BArea.height),
    )

    config.pLabel = pyglet.text.Label(
        text=man.cwd,
        x=BArea.x+10,
        font_size=9,
        y=int(BArea.y + BArea.height/2),
        anchor_y = "center",
        group=group,
        batch=config.BBatch
    )

    @Climb.event
    def on_press():
        man.chdir(man.climbdir(man.cwd))
        config.Plist._group.offset_y = 0
        config.pLabel.text = man.cwd

    config.BContent.append(Climb)
    config.BFrame.add_widget(Climb)


def create_save_gui(config):
    Prssd = Solid_Color(90, 25, color=(100, 100, 100, 255))
    Dprsd = Solid_Color(90, 25, color=(150, 150, 150, 255))
    Hover = Solid_Color(90, 25, color=(125, 125, 125, 255))

    TArea = config.area(config.TPercent)
    PArea = config.area(config.PPercent)

    Entry = TextEntry(
        "Enter File Name", 
        int(TArea.width*0.05), 
        int(TArea.y+TArea.height*0.55), 
        int(TArea.width*0.75),
        color=(125,125,125, 255),
        text_color=(255,255,255,255),
        caret_color=(255,255,255),
        batch=config.TBatch
    )
    Entry._doc.font_size=10
    #Illegal characters for windows
    Entry.illegal_characters = ["\\", "<", ">", ":", "/", "|", "?", "*", "\""]

    Sbttn = TextButton(
        "Save",
        int(TArea.width*0.05 + Entry._width + 10),
        Entry.y,
        Prssd,
        Dprsd,
        Hover,
        batch=config.TBatch
    )

    Cbttn = TextButton(
        "Cancel",
        int(TArea.width*0.05 + Entry._width+10),
        int(TArea.y+TArea.height*0.10),
        Prssd,
        Dprsd,
        Hover,
        batch=config.TBatch
    )

    @Sbttn.event
    def on_press():
        if config.Extension == None: return
        name=Entry._doc.text+config.Extension
        winsave(path=man.cwd, name=name)
        config.on_close()
    
    @Cbttn.event
    def on_press(): config.on_close()

    load_bottom(config)
    load_shortcuts(config)
    load_drop_down_menu(config)
    preload_path_buttons(config)
   
    config.TContent.append(Entry)
    config.TContent.append(Sbttn)
    config.TContent.append(Cbttn)

    config.window.push_handlers(Entry)
    config.TFrame.add_widget(Sbttn)
    config.TFrame.add_widget(Cbttn)


