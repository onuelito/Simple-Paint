import os
import pyglet
import numpy as np
from pyglet.gl import*

class Canvas:
    def __init__(self, window, x, y, width, height):
        self._x     = x
        self._y     = y
        self.width  = width
        self.height = height

        #Resolution
        self.zoom = 1
        self.min_zoom = 0.5
        self.max_zoom = 5.0

        #Textures
        self.data   = np.zeros(dtype='uint32', shape=(width*height,))
        self.data.fill(0xFFFFFFFF)
        self.refresh()

        #Histroy
        self.history_index = 0
        self.history_limit = 20
        self.history = [None]*self.history_limit
        self.history[0] = np.copy(self.data)
        
        self.window = window
        self.pre_width  = self.window.width
        self.pre_height = self.window.height
        window.push_handlers(self)


    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    """
    Drawing setup
    """

    def save_as(self, name="Untitled.png"):

        self.refresh()
        if len(name) == 0 or name[0] == ".": return
        try: name, extension = name.split(".")
        except: print("Extension missing. Enter `.png`"); return
        extension = extension.lower()
        name = name+"."+extension
        formatList = {
            "png": "RGBA",
            #"jpg": "RGB",
            #"bmp": "RGB",
        }
        
        formatImg = "RGBA"
        try: formatImg = formatList[extension]
        except: print("Image format '%s' not supported!"%(extension)); return
        """
        Might be worked on for future extensions
        try: formatImg = formatList[extension]
        except: print("Image format '%s' not supported!"%(extension)); return

        if formatImg == "RGB":
            save_img = np.copy(self.data)
            save_img = save_img - 0xFF000000
            #print(save_img.size, save_img[0:4], self.data[0:4])
            print(save_img)
            save_img = save_img.tobytes()
        """

        save_img = self.data.tobytes()
        save_img = pyglet.image.ImageData(self.width, self.height, formatImg, save_img)

        save_img.save(os.getcwd()+"/"+f"{name}")
        print("[Image saved as \"%s\"]"%name)
        self.window.app_config["MANAGER"]["SAVE_NAME"] = name
        self.window.set_caption("Simple-Paint: "+name)
        return True

    def open(self, name="Untitled.png"):
        self.refresh()
        image = None
        try:
            image   = pyglet.image.load(name)
            image   = image.get_region(0, 0, min(image.width, self.width), min(image.height, self.height))
            rawimg  = image.get_image_data()

            pitch   = rawimg.width * 4
            pixels  = rawimg.get_data("RGBA", pitch)
            pixels  = np.frombuffer(pixels, dtype="uint32")

            #Conversion!!!
            for y in range(0, image.height):
                for x in range(0, image.width):
                    self.data[y*self.width+x] = pixels[y*image.width+x]

            self.refresh()
            self._update()

        except: print(name+" does not exist or is not a '.png' image!")
        return image

    def get_color(self, x, y):
        try:
            x -= int(self.x-self.width*self.zoom/2)
            y -= int(self.y-self.height*self.zoom/2)
            return self.data[y*self.width+x]
        except: return

    def undo(self):
        if self.history_index == 0:
            print("Cannot undo: Minimum index reached!")
            return
        self.history_index -= 1
        self.data = np.copy(self.history[self.history_index])
        self.refresh()

    def redo(self):
        if self.history_index + 1 == self.history_limit or self.history[self.history_index+1] is None:
            print("Cannot redo: Maximum index reached!")
            return
        self.history_index += 1
        self.data = np.copy(self.history[self.history_index])
        self.refresh()


    def _update(self):
        if self.history_index == self.history_limit-1:
            #If history has reached limit
            self.history.append(None)
            self.history.pop(0)
            self.history_index -= 1

        self.history_index += 1
        if self.history_index < self.history_limit -1:
            #Clearing redo history 
            for index in range(self.history_index, self.history_limit):
                self.history[index] = None

        
        self.history[self.history_index] = np.copy(self.data)

    """
    Texture setup
    """
    def refresh(self):
        self.texture = self.data.tobytes()
        self.texture = pyglet.image.ImageData(self.width, self.height, 'RGBA', self.texture)
        self.texutre = self.texture.get_texture()

        self.texture.anchor_x = int(self.width//2)
        self.texture.anchor_y = int(self.height//2)

        self.texture.width = int(self.width)
        self.texture.height= int(self.height)

    def draw(self): 
        glScalef(self.zoom, self.zoom, 0.0)
        self.texture.blit(int(self.x/self.zoom-self.width//2), int(self.y/self.zoom-self.height//2))
        glScalef(1/self.zoom, 1/self.zoom, 0.0)

    def _zoom(self, x, y, scroll_y):
        """
        I have no idea how I made this work but it does
        """

        pre_width, pre_height = self.width*self.zoom, self.height*self.zoom
        new_zoom = min(max(self.zoom+scroll_y/10, self.min_zoom), self.max_zoom)

        dist_x = x - self.x; dist_y = y - self.y
        new_dist_x = (x-self.x)*(new_zoom/self.zoom)
        new_dist_y = (y-self.y)*(new_zoom/self.zoom)

        self.x -= new_dist_x-dist_x
        self.y -= new_dist_y-dist_y

        self.zoom = new_zoom
        self.refresh()

    def reset(self):
        self.zoom = 1
        self.x, self.y = self.pre_width//2, self.pre_height//2

    def clear(self):
        self.data.fill(0xFFFFFFFF)
        self.refresh()

    def on_resize(self, width, height):
        """
        Replacing canvas with resize
        """

        self.x = self.x*width/self.pre_width
        self.y = self.y*height/self.pre_height

        self.pre_width  = width
        self.pre_height = height


