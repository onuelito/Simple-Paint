import pyglet
from pyglet.graphics import OrderedGroup

from .widget import WidgetBase
from .graphics import ScissorGroup

class Frame(WidgetBase):
    """
    Class to encapsulate widgets
    """

    def __init__(self, window, x, y, width, height, anchor_x="left", anchor_y="bottom", group=None, batch=None):

        super().__init__(x, y, width, height, anchor_x=anchor_x, anchor_y=anchor_y)

        self.window = window
        self.batch = batch
        self.widgets = list() #Only classes so fine

        #Previsous width and height of parent
        self.pWidth = window.width if not self._parent else self._parent.width
        self.pHeight= window.height if not self._parent else self._parent.height

        #Group setup
        x_offset, y_offset = self.anchor_offset

        self._group = group or pyglet.graphics.Group()
        self.rgroup = OrderedGroup(self._z, parent=self._group)
        self.fgroup = ScissorGroup(
            x - x_offset,
            y - y_offset,
            width,
            height,
            order=1, 
            parent=self.rgroup
        )
        self.bgroup = OrderedGroup(0, parent=self.rgroup)

        #Background setup

        _background = pyglet.image.SolidColorImagePattern((0,0,0,125))
        _background = _background.create_image(width, height)
        self.background = pyglet.sprite.Sprite(
            _background,
            x - x_offset,
            y - y_offset,
            group=self.bgroup,
            batch=batch
        )


    """
    Properties
    """
    @property
    def x(self):
        return self._x 

    @x.setter
    def x(self, value):
        xO, yO = self.anchor_offset

        self._x = value

        self.fgroup.x = value - xO
        self.background.x = int(self.x - xO)

    @property
    def y(self):
        return self._y 

    @y.setter
    def y(self, value):
        xO, yO = self.anchor_offset

        self._y = value

        self.fgroup.y = value - yO
        self.background.y = int(self.y - yO)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self.rgroup = OrderedGroup(value, parent=self._group)
        x, y = self.bottom_left

        #Background Group Reset
        bgroup = OrderedGroup(0, parent=self.rgroup)
        bgroup.visible = self.bgroup.visible
        self.bgroup = bgroup

        #Foreground Group Reset
        fgroup = ScissorGroup(x, y, self.width, self.height, 1, parent=self.rgroup)
        fgroup.offset_x = self.fgroup.offset_x
        fgroup.offset_y = self.fgroup.offset_y

        self.fgroup = fgroup
        self.background.group = self.bgroup
        self._z = value

        for widget in self.widgets: widget.group = self.fgroup

        
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        scale_x = value/self._width
        self._width = value
        self.background.scale_x *= scale_x

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        scale_y = value/self._height
        self._height = value
        self.background.scale_y *= scale_y

    @property
    def offset_x(self):
        return self.fgroup.offset_x

    @property
    def offset_y(self):
        return self.fgroup.offset_y

    @property
    def background_visible(self):
        return self.background.visible

    @background_visible.setter
    def background_visible(self, value):
        self.background.visible = value

    """
    Special Functions
    """
    def add_widget(self, widget, x=None, y=None, z=None):
        widget.parent = self
        self.widgets.append(widget)

        widget.batch = self.batch
        widget.group = self.fgroup
        widget.z = len(self.widgets) if z == None else z

        x_offset, y_offset = self.anchor_offset

        widget.x = self.x - x_offset+x if x != None else widget.x
        widget.y = self.y - y_offset+y if y != None else widget.y

    def remove_widget(self, widget):
        self.widgets.remove(widget)
        widget.parent = None
        widget.batch = None
        widget.group = None

    def update_groups(self):
        x_offset, y_offset = self.anchor_offset

        self.fgroup.x   = self.x - x_offset
        self.fgroup.y   = self.y - y_offset

        self.fgroup.width = self.width
        self.fgroup.height= self.height

    def move(self, x, y):
        delta_x = x - self.x
        delta_y = y - self.y

        for widget in self.widgets:
            widget.x += delta_x
            widget.y += delta_y

        self.x = x
        self.y = y

    def drag(self, dx, dy):
        self.move(self.x + dx, self.y + dy)

    """
    Window Event (widgets management)
    """
    def on_mouse_press(self, x, y, button, modifiers):
        xo, yo = self.fgroup.offset_x, self.fgroup.offset_y
        if self.mouse_handler == None:
            for widget in self.widgets:
                widget.on_mouse_press(x-xo, y-yo, button, modifiers)
        else:
            if not self._check_hit(x, y):
                if self.mouse_handler.frame == self:
                    self.mouse_handler._remove_frame()
                return
            else: self.mouse_handler.frame = self

            for widget in self.widgets:
                if widget._check_hit(x-xo, y-yo):
                    self.mouse_handler.pwidget = widget

            if self.mouse_handler.pwidget in self.widgets:
                self.mouse_handler.pwidget.on_mouse_press(x-xo, y-yo, button, modifiers)


    def on_mouse_release(self, x, y, button, modifiers):
        xo, yo = self.fgroup.offset_x, self.fgroup.offset_y
        if self.mouse_handler == None:
            for widget in self.widgets: 
                widget.on_mouse_release(x-xo, y-yo, button, modifiers)
        else:
            if self.mouse_handler.pwidget in self.widgets:
                if not self._check_hit(x, y):
                    x, y = self.mouse_handler.pwidget.bottom_left
                    x = x-1
                self.mouse_handler.pwidget.on_mouse_release(x-xo, y-yo, button, modifiers)
                self.mouse_handler._pwidget = None

    def on_mouse_motion(self, x, y, dx, dy):
        xo, yo = self.fgroup.offset_x, self.fgroup.offset_y
        if self.mouse_handler == None:
            for widget in self.widgets:
                widget.on_mouse_motion(x-xo, y-yo, dx, dy)
        else:
            
            if not self._check_hit(x, y):
                if self.mouse_handler.frame == self:
                    self.mouse_handler._remove_frame()
                return
            else: self.mouse_handler.frame = self
            
            if self.mouse_handler.frame != self: return

            for widget in self.widgets:
                if widget._check_hit(x-xo, y-yo) and widget != self.mouse_handler.hwidget:
                    self.mouse_handler._remove_hover()
                    self.mouse_handler.hwidget = widget

            if self.mouse_handler.hwidget in self.widgets:
                self.mouse_handler.hwidget.on_mouse_motion(x-xo, y-yo, dx, dy)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        xo, yo = self.fgroup.offset_x, self.fgroup.offset_y

        if self.mouse_handler == None:
            for widget in self.widgets:
                widget.on_mouse_drag(x-xo, y-yo, dx, dy, button, modifiers)
        else:
            if not self._check_hit(x, y):
                if self.mouse_handler.frame == self:
                    self.mouse_handler._remove_frame()
                return
            else: self.mouse_handler.frame = self
            
            if self.mouse_handler.frame != self: return

            for widget in self.widgets:
                if widget._check_hit(x-xo, y-yo) and widget != self.mouse_handler.dwidget:
                    self.mouse_handler._remove_drag()
                    self.mouse_handler.dwidget = widget

            if self.mouse_handler.dwidget in self.widgets:
                self.mouse_handler.dwidget.on_mouse_drag(x-xo, y-yo, dx, dy, button, modifiers)



    #For TextEntries
    def on_text(self, text):
        for widget in self.widgets:
            widget.on_text(text)

    def on_text_motion(self, motion):
        for widget in self.widgets:
            widget.on_text_motion(motion)
           


    def on_resize(self, width, height):
        """
        Resizing and replacing the Frame and its widgets
        """
        #Old Frame coordinations
        Fbx, Fby = self.bottom_left
        Ftx, Fty = self.top_left
        Fcx, Fcy = self.center


        old_x, old_y = self.x, self.y
        ooffset_x, ooffset_y = self.fgroup.offset_x, self.fgroup.offset_y

        old_width, old_height = self.width, self.height
        #print(self._id, self.width/self.pWidth)
        #new_width, new_height = self.width*width/self.pWidth, self.height*height/self.pHeight
        new_width, new_height = self.width + (width-self.pWidth), self.height + (height-self.pHeight)

        if self.styler.stretch_resolution:
            self.width = new_width if self.styler.stretch_x else old_width
            self.height= new_height if self.styler.stretch_y else old_height

        elif self.styler.fixed_resolution:
            self.width, self.height = self.styler.aspect_ratio_size(new_width, new_height)

        self.x  = old_x*width/self.pWidth if self.styler.sticky_x else old_x
        self.y  = old_y*height/self.pHeight if self.styler.sticky_y else old_y

        for widget in self.widgets:

            #Saving Previous State
            dx, dy = widget.x - old_x, widget.y - old_y
            previous_width, previous_height = widget.width, widget.height

            dpositions = [
                [widget.x - Fbx, widget.y - Fby],
                [widget.x - Ftx, widget.y - Fty],
                [widget.x - Fcx, widget.y - Fcy],
            ]

            #Changing Position
            widget._rel_resize(
                old_width,
                old_height,
            )

            delta_width = widget.width - previous_width
            delta_height= widget.height - previous_height


            widget.x = self.x+dx*self.width/old_width if widget.styler.sticky_x else widget.x
            widget.y = self.y+dy*self.height/old_height if widget.styler.sticky_y else widget.y


            #widget.x = self.x+ (self.width-old_width) if widget.styler.sticky_x else widget.x
            #widget.y = self.y+ (self.height-old_height) if widget.styler.sticky_y else widget.y

            #Alignement if no resizing
            nFbx, nFby = self.bottom_left
            nFtx, nFty = self.top_left #NFT ???
            nFcx, nFcy = self.center

            if delta_width == 0 and widget.styler.sticky_x:
                if widget.anchor_x == 'left': widget.x = nFbx + dpositions[0][0]
                if widget.anchor_x == 'right': widget.x = nFtx+dpositions[1][0]
                if widget.anchor_x == 'center': widget.x = nFcx+dpositions[2][0] 

            if delta_height == 0 and widget.styler.sticky_y:
                if widget.anchor_y == 'bottom': widget.y = nFby + dpositions[0][1]
                if widget.anchor_y == 'top': widget.y = nFty+dpositions[1][1]
                if widget.anchor_y == 'center': widget.y = nFcy+dpositions[2][1]


        self.pWidth = width
        self.pHeight= height

        self.update_groups()


class ScrollFrame(Frame):
    """
    Extension class for `Frame` class to allow scrolling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scroll_x = 0
        self._scroll_y = 0

        self.scroll_x_multiplier = 0
        self.scroll_y_multiplier = 5

        #Scroll limits will be used later
        self.min_scroll_x = None
        self.max_scroll_x = None

        self.min_scroll_y = None
        self.max_scroll_y = None

    @property
    def scroll_x(self):
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value):
        self.fgroup.offset_x = int(value)
        self._scroll_x = value

    @property
    def scroll_y(self):
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value):
        self.fgroup.offset_y = int(value)
        self._scroll_y = value

    def on_mouse_scroll(self, x, y , dx, dy):
        if self.mouse_handler:
            self.mouse_handler.frame = self
            if self.mouse_handler.frame != self: return
        if not self._check_hit(x, y): return
        if self.scroll_x_multiplier != 0: self.scroll_x += dx*self.scroll_x_multiplier
        if self.scroll_y_multiplier != 0: 
            self.scroll_y += dy*self.scroll_y_multiplier
            self.scroll_y = max(0, self.scroll_y)
