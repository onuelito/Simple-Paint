def Config():
    config = {
        "MANAGER": {
            "SAVE_NAME": None,

            "SHORTCUTS": {
                "DESKTOP"   : "~/Desktop",
                "DOCUMENTS" : "~/Documents",
                "HOME"      : "~",
                "PICTURES"  : "~/Pictures",
            }
        },

        "HELP": """
        <center>
        <font face="Retro Gaming">
        [SHORTCUTS]<br/>
        B : Pencil Tool<br/>
        F : Bucket Tool <br/>
        E : Eraser Tool <br/>
        H : Toggle Help <br/>
        R : Reset Canvas<br/>
        P : Color Selector<br/>
        C : Clear Canvas<br/>
        V : Color Picker<br/><br/>

        CTRL + Z : Undo<br/>
        CTRL + Y : Redo<br/>
        CTRL + S : Save<br/>

        CTRL + MouseScroll  : Zoom In/Out<br/>
        ALT  + Mouse Motion : Move Canvas
        </font>
        </center>
        
        """
    }
    return config

