import pyglet
import src.cfuncs as clib

class ToolBase(pyglet.event.EventDispatcher):
    window  = None
    color   = 0xFF000000
    size    = 0

    color_status = [
        [0, 0, 0, 255], #3rd vertex color
        (0, 0) #Offset
    ]

    def set_color_status(self, color_picker):
        self.color_status = [color_picker.select_color, color_picker.delta_triangle]

    def get_color_status(self):
        return self.color_status

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def activate(self):
        return

    def deactivate(self):
        self.window.toolTip.text = "Tool: None"


class Pencil(ToolBase):
    def __init__(self, window):
        self.window = window
        self._pressed = False

        #Pencil Mouse variables
        self.pre_x = 0
        self.pre_y = 0
        self.drawing = False

    def activate(self):
        self.window.toolTip.text = "Pencil: "+str(self.size)+" px"

    def on_mouse_press(self, x, y, button, modifiers):
        self.pre_x = x
        self.pre_y = y

        self.color = self.window.colorP.get_color()
        self.drawing = True
        #self.set_color_status(self.window.colorP)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.drawing: self.drawing = False
        else: return
        self.window.canvas._update()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.drawing: return
        clib.draw(
            self.window.canvas,
            self.color, 
            int(self.size), 
            x, 
            y, 
            self.pre_x, 
            self.pre_y
        )

        self.pre_x = x
        self.pre_y = y
        self.window.canvas.refresh()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.window.key_manager[self.window.key.LSHIFT]:
            return
        self.size = min(max(0, self.size+scroll_y), 50)
        self.activate()
        #print("Pencil Size:", self.size)


class Bucket(ToolBase):
    def __init__(self, window):
        self.window = window
        self.filling = False

    def on_mouse_press(self, x, y, button, modifiers):

        self.color = self.window.colorP.get_color()
        self.filling = True
        #self.set_color_status(self.window.colorP)

        clib.flood_fill(
            self.window.canvas,
            self.color,
            x,
            y,
        )
        self.window.canvas.refresh()

    def activate(self):
        self.window.toolTip.text = "Bucket: All/Nothing px"

    def on_mouse_release(self, x, y, button, modifiers):
        if self.filling: self.filling = False
        else: return
        self.window.canvas._update()

class Eraser(ToolBase):
    def __init__(self, window):
        self.window = window
        self.color = 0xFFFFFFFF

        #Pencil Mouse variables
        self.pre_x = 0
        self.pre_y = 0

    def activate(self):
        self.window.toolTip.text = "Eraser: "+str(self.size)+" px"

    def on_mouse_press(self, x, y, button, modifiers):
        self.pre_x = x
        self.pre_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        self.window.canvas._update()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        clib.draw(
            self.window.canvas,
            self.color, 
            int(self.size), 
            x, 
            y, 
            self.pre_x, 
            self.pre_y
        )

        self.pre_x = x
        self.pre_y = y
        self.window.canvas.refresh()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.window.key_manager[self.window.key.LSHIFT]:
            return
        self.size = min(max(0, self.size+scroll_y), 50)
        self.activate()
        #print("Eraser Size:", self.size)

class Picker(ToolBase):
    def __init__(self, window):
        self.window = window
 
    def activate(self):
        self.window.toolTip.text = "Picker: N/A px"
   

    def on_mouse_press(self, x, y, button, modifiers):
        color = self.window.canvas.get_color(x, y)
        if color: 
            red     = color & 255
            green   = (color >> 8)  & 255
            blue    = (color >> 16) & 255
            self.window.colorP.set_color((red, green, blue, 255))
        self.window.tool_manager.notool()
        self.window.pickerB.pressed = False
