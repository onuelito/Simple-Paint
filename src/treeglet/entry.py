"""
File dedicated for customizing TextEntry specificaly
"""

import pyglet
from pyglet.gl import*
import pyglet.clock as clock
from pyglet.text.caret import Caret
from pyglet.graphics import Batch, OrderedGroup
from pyglet.text.layout import*

from .widget import WidgetBase, WidgetStyler

pyglet.options["debug_gl"] = False

class CustomLayoutGroup(IncrementalTextLayoutGroup):

    def set_state(self):
        glPushAttrib(GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_CURRENT_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_SCISSOR_TEST)
        glScissor(
            int(self._clip_x-1), 
            int(self._clip_y - self._clip_height), 
            int(self._clip_width+1), 
            int(self._clip_height),
        )

        glTranslatef(self.translate_x, self.translate_y, 0)

    def unset_state(self):
        glTranslatef(-self.translate_x, -self.translate_y, 0)
        glPopAttrib()
        glDisable(GL_SCISSOR_TEST)

class CustomLayout(IncrementalTextLayout):
    
    def _init_groups(self, group):
        self.top_group = CustomLayoutGroup(group)
        self.background_group = pyglet.graphics.OrderedGroup(0, self.top_group)
        self.foreground_group = TextLayoutForegroundGroup(1, self.top_group)
        self.foreground_decoration_group =TextLayoutForegroundDecorationGroup(2, self.top_group)

class TextEntry(WidgetBase):
    """
    TextEntry
    """

    def __init__(self, text, x, y, background, color=(0, 0, 0, 255), caret_color=(0,0,0), group=None, batch=None):

        super().__init__(x, y, background.width, background.height)
        
        self._document = pyglet.text.document.UnformattedDocument(text)
        self._document.set_style(
            0, 
            len(self._document.text), 
            dict(
                color=(0,0,0,255),
                font_size=12,
                )
            )

        self._batch  = batch
        self.caret_color = caret_color

        self.entry_limit = -1
        self.illegal_characters = list()
        self.authorized_characters = list()

        self._group = OrderedGroup(self._z, parent=group)
        self.fgroup = OrderedGroup(1, parent=self._group)
        self.bgroup = OrderedGroup(0, parent=self._group)

        self._sprite = pyglet.sprite.Sprite(
            background,
            x,
            y,
            group=self.bgroup,
            batch=self._batch
        )

        self._layout_x = 0 
        self._layout_y = 0


        self._init_caret() 
        self._layout.x = x
        self._layout.y = y
        self._focus = False

    """
    Properties
    """
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        xO, yO = self.anchor_offset
        self._sprite.x = value - xO
        self._x = value
        self.layout_x = self.layout_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        xO, yO = self.anchor_offset
        self._sprite.y = value - yO
        self._y = value

        self.layout_y = self.layout_y
        

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._group = OrderedGroup(value, parent=self._group.parent)
        self.bgroup = OrderedGroup(0, parent=self._group)
        self.fgroup = OrderedGroup(1, parent=self._group)

        posin = self._caret.position
        focus = self._focus
        x = self._layout.x
        y = self._layout.y

        self._set_focus(False)
        self._layout.delete()
        self._caret.delete()

        self._init_caret(position=posin, focus=focus)
        self._layout.x = x
        self._layout.y = y

        self._sprite.group = self.bgroup
        self._z = value

    @property
    def text(self):
        return self._layout.document.text

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._sprite.scale_x *= value/self._width
        self._layout.width = value
        self._width = value
        self.layout_x = self.layout_x

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._sprite.scale_y *= value/self._height
        self._layout.height = value
        self._height = value
        self.layout_y = self.layout_y

    @property
    def group(self):
        return self._group.parent

    @group.setter
    def group(self, value):
        self._group = OrderedGroup(self.z, parent=value)
        self.z = self.z

    @property
    def batch(self):
        return self._batch

    @batch.setter
    def batch(self, value):
        self._batch = value
        self._sprite.batch = value
        self._layout.batch = value


    def _set_focus(self, value):
        self._focus = value
        self._caret.visible = value

    """
    Layout properties
    """
    @property
    def layout_x(self):
        return self._layout_x

    @layout_x.setter
    def layout_x(self, value):
        self._layout_x = value

        if type(value) == str:
            if value.endswith("%"): value = self.width * (int(value[:-1]) / 100)
            else: raise Exception("x value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._layout.width = self._width - value
        self._layout.x = self.x - xO + value



    @property
    def layout_y(self):
        return self._layout_y

    @layout_y.setter
    def layout_y(self, value):
        self._layout_y = value
        
        if type(value) == str:
            if value.endswith("%"): value = self.height * (int(value[:-1]) / 100)
            else: raise Exception("y value must be a string ending with % or a number")

        xO, yO = self.anchor_offset
        self._layout.y = self.y - yO + value

        

    """
    Helper functions
    """
    def _init_caret(self, position=0, focus=False):
        self._layout = CustomLayout(
            self._document,
            self.width,
            self.height,
            multiline=False,
            batch=self._batch,
            group=self.fgroup,
        )

        self._caret = Caret(
            self._layout,
            batch=self._batch,
            color=self.caret_color
        )

        self._caret._position = position 
        self._set_focus(focus)


    def _rel_resize(self, pp_width, pp_height):
        self._default_resize(pp_width, pp_height)
        #Refreshing text
        self.layout_x = self.layout_x
        self.layout_y = self.layout_y

    def style_document(self, dictionnary):
        """
        Needs some work innit?
        """
        self._document.set_style(0, len(self._document.text), dictionnary)

    """
    Text Events
    """
    def on_text(self, text):
        if len(self.illegal_characters) > 0 and text in self.illegal_characters:
            return
        if len(self.authorized_characters) > 0 and text not in self.authorized_characters:
            return

        if self.entry_limit >= 0 and len(self._layout.document.text) >= self.entry_limit:
            return

        if not self._focus: return
        if text in ('\r', '\n'):
            self.dispatch_event('on_commit', self._layout.document.text)
            self._set_focus(False)
            return
        self._caret.on_text(text)

    def on_text_motion(self, motion):
        if not self._focus: return
        self._caret.on_text_motion(motion)


    """
    Mouse Events
    """

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.enabled: return
        if self._check_hit(x, y):
            self._set_focus(True)
            self._caret.on_mouse_press(x, y, button, modifiers)
        else: self._set_focus(False)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.enabled: return
        self._caret.on_mouse_drag(x, y, dx, dy, button, modifiers)



TextEntry.register_event_type("on_commit")
