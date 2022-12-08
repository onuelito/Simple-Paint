import pyglet
from pyglet.gl import*

import src.windows.gui as gui
import src.windows.manager as man
from src.core.window import window

class Mouse:
    x   = 0
    y   = 0

class Configuration:
    class _GuiPercentage:
        def __init__(self, x, y, w, h):
            self.x, self.y = x, y
            self.w, self.h = w, h
    class _Area:
        def __init__(self, x, y, width, height):
            self.x, self.y          = x, y
            self.width, self.height = width, height

    TPercent = _GuiPercentage(0.00, 0.85, 1.00, 0.15)
    SPercent = _GuiPercentage(0.00, 0.05, 0.20, 0.80)
    PPercent = _GuiPercentage(0.20, 0.05, 0.80, 0.80)
    BPercent = _GuiPercentage(0.00, 0.00, 1.00, 0.05)

    #Windows default settings
    window      = None
    minWidth    = 640
    minHeight   = 480
    scale_x     = 1
    scale_y     = 1
    
    #Lists
    TContent = list()
    DContent = list()
    PContent = list()
    BContent = list()
    SContent = list()

    Plist   = None #Path lists for buttons
    PathButton = list()

    #Graphics
    TBatch  = None
    SBatch  = None
    PBatch  = None
    BBatch  = None
    DBatch  = None #Background batch

    TFrame  = None
    PFrame  = None
    SFrame  = None
    BFrame  = None
    Extension   = None
    pLabel      = None


    def area(self, percent):
        """
        Function to get area of GuiPercentage for resizing and
        position gui.
        """
        x = percent.x*self.window.width
        y = percent.y*self.window.height
        w = percent.w*self.window.width
        h = percent.h*self.window.height

        return self._Area(x, y, w, h)

    def on_resize(self, width, height):
        self.scale_x = width/self.minWidth
        self.scale_y = height/self.minHeight

    def on_close(self):

        pyglet.clock.unschedule(self.update)
        self.DContent.clear()
        self.TContent.clear()
        self.TFrame = None
        for button in self.PathButton: gui.detach_button(button)
        self.PathButton.clear()
        self.PContent.clear()

        self.window.remove_handler('on_draw', self.on_draw)
        self.window.clear()
        self.window.close()
        self.window = None
        man.terminate()

    def on_draw(self):
        glClearColor(0.0, 0.1, 0.1, 1.0)
        self.window.clear()
        
        glScalef(self.scale_x, self.scale_y, 0)

        self.DBatch.draw()
        self.BBatch.draw()
        self.PBatch.draw()
        self.SBatch.draw()
        self.TBatch.draw()

        glScalef(1/self.scale_x, 1/self.scale_y, 0)

    def update(self, dt):
        if not man.update(): return
        gui.load_content(self)
        self.pLabel.text = man.cwd

def create_window(config, caption="Save as"):
    config.window = pyglet.window.Window(
        config.minWidth, 
        config.minHeight,
        resizable=True, 
        caption=caption
    )
    config.window.clear()
    config.window.switch_to()
    config.window.set_minimum_size(config.minWidth, config.minHeight)

def attach_events(config):
    config.window.set_handler('on_draw', config.on_draw)
    config.window.set_handler('on_close', config.on_close)
    config.window.set_handler('on_resize', config.on_resize)

def setup_background(config):
    """
    Background drawing
    """
    TArea = config.area(config.TPercent)
    SArea = config.area(config.SPercent)
    PArea = config.area(config.PPercent)
    BArea = config.area(config.BPercent)

    TColor = (175, 175, 175)
    SColor = (125, 125, 125)
    PColor = (150, 150, 150)
    BColor = (100, 100, 100)
    
    TBackground = pyglet.shapes.Rectangle(
        TArea.x,
        TArea.y,
        TArea.width,
        TArea.height,
        color = TColor,
        batch = config.DBatch
    )
    SBackground = pyglet.shapes.Rectangle(
        SArea.x,
        SArea.y,
        SArea.width,
        SArea.height,
        color = SColor,
        batch = config.DBatch
    )
    PBackground = pyglet.shapes.Rectangle(
        PArea.x,
        PArea.y,
        PArea.width,
        PArea.height,
        color = PColor,
        batch = config.DBatch
    )
    BBackground = pyglet.shapes.Rectangle(
        BArea.x,
        BArea.y,
        BArea.width,
        BArea.height,
        color = BColor,
        batch = config.DBatch
    )

    config.DContent.append(TBackground)
    config.DContent.append(SBackground)
    config.DContent.append(PBackground)
    config.DContent.append(BBackground)


def setup_save_window(config):
    """
    Function to attach events from configuration class to the
    window and stuff.
    """
    config.TBatch  = pyglet.graphics.Batch()
    config.SBatch  = pyglet.graphics.Batch()
    config.PBatch  = pyglet.graphics.Batch()
    config.BBatch  = pyglet.graphics.Batch()
    config.DBatch  = pyglet.graphics.Batch() #Background batch

    config.SFrame = gui.CustomFrame(config.window)
    config.TFrame = gui.CustomFrame(config.window)
    config.PFrame = gui.CustomFrame(config.window)
    config.BFrame = gui.CustomFrame(config.window)

    gui.create_save_gui(config)


    attach_events(config)
    setup_background(config)

    man.update()
    gui.load_content(config)
    pyglet.clock.schedule_interval(config.update, 1/15)

