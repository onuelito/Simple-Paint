import pyglet
from pyglet.graphics import OrderedGroup, Batch

class WidgetStyler:
    """
    Style class to give some swagger to your widgets
    """

    target = None

    #Position arguments
    sticky_x    = True
    sticky_y    = True

    #Resolutions
    _fixed_resolution   = False
    _stretch_resolution = False

    #Resolution arguments
    stretch_x   = False
    stretch_y   = False
    fill_x      = False
    fill_y      = False


    """
    Position Modifiers
    """
    @property
    def sticky(self):
        return True if self.sticky_x and self.sticky_y else False

    @sticky.setter
    def sticky(self, value):
        self.sticky_x = value
        self.sticky_y = value

    """
    Resolution
    """
    @property
    def aspect_ratio(self):
        from fractions import Fraction
        eq = Fraction(self.target.width/self.target.height).limit_denominator()

        return eq.numerator, eq.denominator

    def aspect_ratio_size(self, size_x, size_y):
        """
        Setting up aspect ratio
        """

        aspect_x, aspect_y = self.aspect_ratio
        width   = self.target.width
        height  = self.target.height

        if aspect_x < aspect_y:
            width   = size_x
            height  = size_x*aspect_y/aspect_x
        else:
            height  = size_y
            width   = size_y*aspect_x/aspect_y

        return width, height

    """
    Size modifiers
    """
    @property
    def stretch_resolution(self):
        return self._stretch_resolution

    @stretch_resolution.setter
    def stretch_resolution(self, value):
        self.stretch_x = value
        self.stretch_y = value

        self._stretch_resolution = value
        self._fixed_resolution = not value if value==True else self._fixed_resolution

    @property
    def fixed_resolution(self):
        return self._fixed_resolution

    @fixed_resolution.setter
    def fixed_resolution(self, value):
        self._fixed_resolution = value
        self._stretch_resolution = not value if value==True else self._stretch_resolution



class WidgetBase(pyglet.gui.WidgetBase):
    """
    An extenstion to the `pyglet.gui.widget.WidgetBase` class to fit
    the features of treeglet
    """

    def __init__(self, x, y, width, height, anchor_x="left", anchor_y="bottom"):
        super().__init__(x, y, width, height)

        self.mouse_handler = None
        self._parent    = None
        self._visible   = True
        self._z     = 0 #Z index of widget
        self._id    = "widget"

        self.styler = WidgetStyler()
        self.styler.target = self

        #Alignement
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

    @property
    def bottom_left(self):
        xO, yO = self.anchor_offset

        return self._x - xO, self._y - yO

    @property
    def center(self):
        xO, yO = self.anchor_offset

        return self._x - xO+self._width//2, self._y - yO+self._height//2
    
    @property
    def top_left(self):
        xO, yO = self.anchor_offset

        return self._x - xO+self._width, self._y - yO+self._height


    @property
    def anchor_offset(self):
        x = 0 if self.anchor_x=='left' else self._width
        y = 0 if self.anchor_y=='bottom' else self._height

        x = self._width//2 if self.anchor_x=='center' else x
        y = self._height//2 if self.anchor_y=='center' else y
        return x, y

    def style(self, **kwargs):
        for var, value in kwargs.items():
            setattr(self.styler, var, value)

    @property
    def absolute_z(self):
        if self.parent: return self.parent.z
        else: return self.z

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    """
    Slight change
    """
    def _default_resize(self, pp_width, pp_height):
        """
        Relative resize
        Function to resize widget based on parent's changes.

        Properties
        `pp_width`  : Parent Previous Width
        `pp_height` : Parent Previous Height
        """

        new_width  = self.width*self.parent.width/pp_width if not self.styler.fill_x else self.width + (self.parent.width-pp_width)
        new_height = self.height*self.parent.height/pp_height if not self.styler.fill_y else self.height + (self.parent.height-pp_height)

        if self.styler.stretch_resolution == True:
            self.width  = new_width if self.styler.stretch_x else self.width
            self.height = new_height if self.styler.stretch_y else self.height
        elif self.styler.fixed_resolution == True:
            self.width, self.height = self.styler.aspect_ratio_size(new_width, new_height)
                      
    def _check_hit(self, x, y):
        bx, by = self.bottom_left
        return bx < x < bx + self._width and by < y < by + self._height
        

class PushButton(WidgetBase):

    def __init__(self, x, y, depressed, pressed, hover, anchor_x="left", anchor_y="bottom", group=None, batch=None):

        super().__init__(x, y, depressed.width, depressed.height, anchor_x=anchor_x, anchor_y=anchor_y)

        self._batch = batch or Batch()
        self._group = OrderedGroup(0, parent=group)
        bgroup      = OrderedGroup(0, parent=self._group)

        #Images
        self._himage = hover
        self._pimage = pressed
        self._dimage = depressed

        self._sprite = pyglet.sprite.Sprite(
            depressed,
            x,
            y,
            group=bgroup,
            batch=self._batch
        )

        self._pressed = False

    """
    Properties
    """

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        xO, yO  = self.anchor_offset
        self._sprite.x = value - xO
        self._x = value


    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        xO, yO = self.anchor_offset
        self._sprite.y = value - yO
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._group = OrderedGroup(value, parent=self._group.parent)
        bgroup = OrderedGroup(0, parent=self._group)
        self._sprite.group = bgroup
        self._z = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._sprite.scale_x *= value/self._width
        self._width = value
        
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._sprite.scale_y *= value/self._height
        self._height = value

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value


    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, value):
        self._group = OrderedGroup(self.z, parent=value)
        self._group.visible = self.visible
        bgroup = OrderedGroup(0, parent=self._group)
        self._sprite.group = bgroup

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self._batch = value
        self._sprite.batch = value

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        self._group.visible = value


    def _check_hit(self, x, y):
        xO, yO = self.anchor_offset
        return self._x < x+xO < self._x + self._width and self._y < y+yO < self._y + self._height

    """
    Custom function
    """
    def _rel_resize(self, pp_width, pp_height):
        """
        Relative resize
        Function to resize widget based on parent's changes.

        Properties
        `pp_width`  : Parent Previous Width
        `pp_height` : Parent Previous Height
        """
        self._default_resize()
    
    """
    Window Events
    """

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.enabled or not self.visible or not self._check_hit(x,y):
            return
        self.pressed = True
        self._sprite.image = self._pimage

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.enabled or not self.visible or not self.pressed:
            return
        self.pressed = False
        if self._check_hit(x, y): 
            self.dispatch_event("on_click")
        self._sprite.image = self._himage if self._check_hit(x, y) else self._dimage

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.enabled or self.pressed:
            return
        self._sprite.image = self._himage if self._check_hit(x, y) else self._dimage

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.enabled or self.pressed:
            return
        self._sprite.image = self._himage if self._check_hit(x, y) else self._dimage

PushButton.register_event_type("on_click")

class ToggleButton(PushButton):
    """
    Extension class from pyglet.gui.ToggleButton
    """

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value
        self._sprite.image = self._dimage

    def _get_release_image(self, x, y):
        return self._himage if self._check_hit(x, y) else self._dimage

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.enabled or not self._check_hit(x, y):
            return
        self._pressed = not self._pressed
        self._sprite.image = self._pimage if self.pressed else self._get_release_image(x, y)
        self.dispatch_event("on_toggle", self.pressed)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.enabled or self._pressed:
            return

        self._sprite.image = self._get_release_image(x, y)

ToggleButton.register_event_type("on_toggle")

