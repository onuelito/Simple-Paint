import pyglet
from .tools import*

class ToolManager(pyglet.event.EventDispatcher):
    """
    Core class to manager tool activity
    """

    def __init__(self, window):
        self.window = window
        self._tools  = {
            TOOL_ID.NOTOOL: None,
            TOOL_ID.PENCIL: Pencil(window),
            TOOL_ID.ERASER: Eraser(window),
            TOOL_ID.BUCKET: Bucket(window),
            TOOL_ID.PICKER: Picker(window),
        }
        self._tool = TOOL_ID.NOTOOL

    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, value):
        if self._tool: self._tool.deactivate()
        self._tool = self._tools[value] 
        if self._tool != None: self._tool.activate()
        if self._tool == self._tools[TOOL_ID.NOTOOL] or self._tool == self._tools[TOOL_ID.ERASER]:
            return
           
        color, delta = self._tool.get_color_status()
        #self.window.colorP.delta_triangle = delta
        #self.window.colorP.set_color(color)

        #Blue    = (self._tool.color >> 8) & 255 
        #Green   = (self._tool.color >> 16) &255
        #Red     = (self._tool.color >> 32) &255
        #Alpha   = 255
        #self.window.colorP.set_color([Red, Green, Blue, Alpha])
    
    def notool(self):
        self.tool = TOOL_ID.NOTOOL 

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.tool or self.window.colorP.focus or self.window.mouse_handler.frame != None: 
            return
        
        self.tool.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.tool or self.window.colorP.focus: return
        self.tool.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.tool or self.window.colorP.focus: return
        self.tool.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.tool or self.window.colorP.focus: return
        self.tool.on_mouse_drag(x, y, dx, dy, button, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.tool or self.window.colorP.focus: return
        self.tool.on_mouse_scroll(x, y, scroll_x, scroll_y)


class _ID:
    NOTOOL = 0
    PENCIL = 1
    ERASER = 2
    BUCKET = 3
    PICKER = 4

TOOL_ID = _ID()

import os

class Navigator(pyglet.event.EventDispatcher):
    """
    Monitroring Current Directory and it's content
    """

    def __init__(self):
        self.cwd = os.getcwd()

        #Content
        self.dirts = set()
        self.files = set()

    def climbdir(self, path=None):
        path = path or self.cwd
        return os.path.abspath(os.path.join(path, os.pardir))

    def checkdir(self, path=None):
        path = path or self.cwd
        while not os.path.exists(path):
            path = self.climbdir(path)

        os.chdir(path)
        self.cwd = path

    def chdir(self, path):
        
        #Permission checking
        if not os.access(path, os.R_OK): return
        if not os.access(path, os.W_OK): return
        if not os.access(path, os.X_OK): return
        if not os.access(path, os.X_OK | os.W_OK): return

        #os.chdir(path)
        os.chdir(path)
        self.cwd = os.getcwd()
        self.update(0) #Force delay

    def _get_content(self, path=None, content_limit=100):
        path = path or self.cwd

        cdirts = list()
        cfiles = list()

        for content in os.listdir(path):
            if content_limit == 0: break
            if content.startswith("."):
                continue
            path = os.path.join(self.cwd, content)
            if os.path.isdir(path):
                cdirts.append(content)
                content_limit -= 1
                continue
            else:
                cfiles.append(content)
                content_limit -= 1

        return cdirts, cfiles

    def update(self, dt):
        self.checkdir(self.cwd)
        DIRTS, FILES = self._get_content()
        if sorted(self.dirts) != sorted(DIRTS) or sorted(self.files) != sorted(FILES): 
            self.dirts = DIRTS; self.files = FILES
            self.dispatch_event("on_content_change", self.dirts, self.files)


Navigator.register_event_type("on_content_change")



