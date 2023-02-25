import pyglet
from pyglet.gl import*
from pyglet.graphics import OrderedGroup

class ScissorGroup(OrderedGroup):
    def __init__(self, x, y, width, height, order=0, parent=None):
        super().__init__(order=order, parent=parent)
        self.x  = x
        self.y  = y

        self.width  = width
        self.height = height

        self.offset_x = 0
        self.offset_y = 0

    def set_state(self):
        glEnable(GL_SCISSOR_TEST)
        glTranslatef(self.offset_x, self.offset_y, 0.0)
        glScissor(
            int(max(1, self.x)),
            int(max(1, self.y)),
            int(max(1, self.width)),
            int(max(1, self.height)),
        )

    def unset_state(self):
        glTranslatef(-self.offset_x, -self.offset_y, 0.0)
        glDisable(GL_SCISSOR_TEST)

