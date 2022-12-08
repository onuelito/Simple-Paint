import src.gui.toolbar as toolbar
import src.tools.ids as toolID

#Positions
x, y, px, py = [0]*4

#Custom variables
target_gui = None
target_win = None
tool = None #The mouse is holding the tool no?

#Updating buttons in GUI
def manage_toolbar(ID):
    #Pencil Button
    if ID == toolID.PENCIL:
        toolbar.pencil_button._pressed = True
        toolbar.pencil_button._sprite.image = toolbar.pencil_button._pressed_img
    else:
        toolbar.pencil_button._pressed = False
        toolbar.pencil_button._sprite.image = toolbar.pencil_button._depressed_img

    #Bucket Button
    if ID == toolID.BUCKET:
        toolbar.bucket_button._pressed = True
        toolbar.bucket_button._sprite.image = toolbar.bucket_button._pressed_img
    else:
        toolbar.bucket_button._pressed = False
        toolbar.bucket_button._sprite.image = toolbar.bucket_button._depressed_img

    #Eraser Button
    if ID == toolID.ERASER:
        toolbar.eraser_button._pressed = True
        toolbar.eraser_button._sprite.image = toolbar.eraser_button._pressed_img
    else:
        toolbar.eraser_button._pressed = False
        toolbar.eraser_button._sprite.image = toolbar.eraser_button._depressed_img

def set_toolmode(ID):
    print("Set tool mode to: "+toolID.NAMES[ID])
    global tool; tool = ID

    #Managing buttons
    manage_toolbar(ID)
