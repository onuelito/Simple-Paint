import os
import src.windows.config as ManCfg

dirts   = list() #Directories
files   = list() #Files (others)
cwd     = None #Current Working Directory
context = None
content_limit = 100 #How much buttons can be drawn
EntryDefaultText = "Enter File Name"

def chdir(path):
    global cwd
  
    #Permission checking
    if not os.access(path, os.R_OK): return
    if not os.access(path, os.W_OK): return
    if not os.access(path, os.X_OK): return
    if not os.access(path, os.X_OK | os.W_OK): return

    os.chdir(path)
    cwd = os.getcwd()

def climbdir(path):
    return os.path.abspath(os.path.join(path, os.pardir))

def checkpath(path):
    """
    Function to check if path exists and jumping to
    parent directory in case not
    """
    global cwd

    while not os.path.exists(path):
        path = climbdir(path)

    cwd = path

def get_content(path):
    global dirts
    global files
    cdirts = list()
    cfiles = list()

    index = 0
    for content in os.listdir(path):
        if index == content_limit: break
        if content.startswith("."):
            continue
        path = os.path.join(cwd, content)
        if os.path.isdir(path):
            cdirts.append(content)
            index += 1
            continue
        else: 
            cfiles.append(content)
            index += 1
    
    return cdirts, cfiles

def update():
    global dirts
    global files

    checkpath(cwd)
    cdirts, cfiles = get_content(cwd)
    if cdirts == dirts and cfiles == files: 
        return False
    dirts = cdirts
    files = cfiles

    return True

def terminate():
    global context
    dirts.clear()
    files.clear()
    context = None

def make_save_window():
    global cwd
    global context

    if context != None: return
    
    if cwd == None: cwd = os.getcwd()
    if not os.path.exists(cwd): chdir(climbdir(cwd))
    context = ManCfg.Configuration()
    ManCfg.create_window(context)
    ManCfg.setup_save_window(context)
