"""
This section is dedicated for a list of custom classes that can be used as reference
for creating your own classes.
"""

import pyglet
from pyglet.graphics import OrderedGroup, Batch
from .widget import PushButton, ToggleButton

"""
Push Button Custom classes
"""

class TextButton(PushButton):
    """
    Extension class of PushButton to support text. Can be used as a reference
    to create cusom PushButtons
    """

    def __init__(self, text, x, y, depressed, pressed, hover, anchor_x="left", anchor_y="bottom", group=None, batch=None):

        super().__init__(x, y, depressed, pressed, hover, anchor_x=anchor_x, anchor_y=anchor_y, group=group, batch=batch)
        #Setting up label and group
        self._text_x    = 0 #X positions an be in %
        self._text_y    = 0 #Y positons can be in %

        fgroup = OrderedGroup(1, parent=self._group)
        self._label = pyglet.text.Label(text=text, x=x, y=y, group=fgroup, batch=batch)

    """
    Overwritting Properties
    """

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        xO, yO  = self.anchor_offset
        delta_x = value - self._x

        self._sprite.x = int(value - xO)
        self._label.x += delta_x
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        xO, yO = self.anchor_offset
        delta_y = value - self._y

        self._sprite.y = value - yO
        self._label.y += delta_y
        self._y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._group = OrderedGroup(value, parent=self._group.parent)
        bgroup = OrderedGroup(0, parent=self._group)
        fgroup = OrderedGroup(1, parent=self._group)

        self._label._init_groups(fgroup)
        self._label._update()

        self._sprite.group = bgroup
        self._z = value

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, value):
        self._group = OrderedGroup(self.z, parent=value)
        bgroup = OrderedGroup(0, parent=self._group)
        fgroup = OrderedGroup(1, parent=self._group)

        self._label._init_groups(fgroup)
        self._label._update()
        self._sprite.group = bgroup

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self._batch = value
        self._sprite.batch = value
        self._label.batch = value


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
        self._default_resize(pp_width, pp_height)   
        #Refreshing text
        self.text_x = self.text_x
        self.text_y = self.text_y

    """
    Label Setup
    """
    @property
    def text_x(self):
        return self._text_x

    @text_x.setter
    def text_x(self, value):
        self._text_x = value

        if type(value) == str:
            if value.endswith("%"): value = self.width * (int(value[:-1]) / 100)
            else: raise Exception("x value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._label.x = self.x - xO + value

    @property
    def text_y(self):
        return self._text_y

    @text_y.setter
    def text_y(self, value):
        self._text_y = value
        
        if type(value) == str:
            if value.endswith("%"): value = self.height * (int(value[:-1]) / 100)
            else: raise Exception("y value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._label.y = self.y - yO + value

    def style_text(self, **kwargs):
        for var, value in kwargs.items():
            setattr(self._label, var, value)


class IconButton(PushButton):
    """
    Extension class of the PushButton class to display icons onto the button
    """

    def __init__(self, icon, x, y, depressed, pressed, hover, anchor_x="left", anchor_y="bottom", group=None, batch=None):

        super().__init__(x, y, depressed, pressed, hover, anchor_x=anchor_x, anchor_y=anchor_y, group=group, batch=batch)

        class CustomSprite(pyglet.sprite.Sprite):
            """
            Extension class of the pyglet.sprite.Sprite to allow anchoring
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.anchor_x = "left"
                self.anchor_y = "bottom"

            @property
            def x(self):
                return self._x

            @x.setter
            def x(self, value):
                xO, yO = self.anchor_offset

                self._x = value - xO
                self._update_position()

            @property
            def y(self):
                return self._y

            @y.setter
            def y(self, value):
                xO, yO = self.anchor_offset

                self._y = value - yO
                self._update_position()

            @property
            def anchor_offset(self):
                xO = self.width if self.anchor_x == "right" else 0
                yO = self.height if self.anchor_y == "top" else 0

                xO = self.width//2 if self.anchor_x == "center" else xO
                yO = self.height//2 if self.anchor_y == "center" else yO

                return xO, yO

        #Exclusive Properties
        self._icon = icon
        fgroup = OrderedGroup(1, parent=self._group)
        self._isprite = CustomSprite(
            icon,
            x,
            y,
            group=fgroup,
            batch=self._batch
        )

        self._icon_x = 0
        self._icon_y = 0


    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        iX, iY = self._isprite.anchor_offset
        xO, yO  = self.anchor_offset
        delta_x = value - self._x

        self._sprite.x = value - xO
        self._isprite.x += delta_x + iX
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        iX, iY = self._isprite.anchor_offset
        xO, yO = self.anchor_offset
        delta_y = value - self._y

        self._sprite.y = value - yO
        self._isprite.y += delta_y + iY
        self._y = value       

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._group = OrderedGroup(value, parent=self._group.parent)
        bgroup = OrderedGroup(0, parent=self._group)
        fgroup = OrderedGroup(1, parent=self._group)

        self._sprite.group = bgroup
        self._isprite.group = fgroup
        self._z = value

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, value):
        self._group = OrderedGroup(self.z, parent=value)
        bgroup = OrderedGroup(0, parent=self._group)
        fgroup = OrderedGroup(1, parent=self._group)

        self._sprite.group = bgroup
        self._isprite.group = fgroup

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self._batch = value
        self._sprite.batch = value
        self._isprite.batch = value
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
        self._default_resize(pp_width, pp_height)
        #Refreshing Icon
        self.icon_x = self.icon_x
        self.icon_y = self.icon_y
    """
    Icon setup
    """
    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self._isprite.image = value

    @property
    def icon_x(self):
        return self._icon_x

    @icon_x.setter
    def icon_x(self, value):
        self._icon_x = value

        if type(value) == str:
            if value.endswith("%"): value = self.width * (int(value[:-1]) / 100)
            else: raise Exception("x value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._isprite.x = self.x - xO + value

    @property
    def icon_y(self):
        return self._icon_y

    @icon_y.setter
    def icon_y(self, value):
        self._icon_y = value
        
        if type(value) == str:
            if value.endswith("%"): value = self.height * (int(value[:-1]) / 100)
            else: raise Exception("y value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._isprite.y = self.y - yO + value



    def style_icon(self, **kwargs):
        for var, value in kwargs.items():
            setattr(self._isprite, var, value)


"""
Toggle CustomButton
"""
class IconToggleButton(ToggleButton, IconButton):
    pass

class TextToggleButton(ToggleButton, TextButton):
    pass
