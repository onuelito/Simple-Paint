import src.tools as tools

#Much better
NOTOOL=0
PENCIL=1
BUCKET=2
ERASER=3

#Has to be in order
MODULES = [
    None, # :(
    tools.pencil,
    tools.bucket,
    tools.eraser
]

#For wheel action
RESIZABLES = [
    PENCIL,
    ERASER
]


#For output reasons
NAMES = [
    "NOTOOL",
    "Pencil",
    "Bucket",
    "Eraser"
]
