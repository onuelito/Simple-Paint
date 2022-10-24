# Simple-Paint #
Simple Paint is an open-source project written in Python and C which's goal is being easy to modify, minimalist and not being heavily dependencies reliant.<br/>

## System requirements ##
**Linux:** You will need to have installed `gcc` on your Linux distribution. It can be done using your package manager. For instance:
<h5>On Arch based distributions</h5>

```
sudo pacaman -S gcc
```
**Windows:** You will need to have installed on your computer a C compiler. For instance by installing Visual Studio with the C/C++ tools in your machine.

**Mac OS:** :(
##
### Running the application ###
Open the terminal in the project directory and type the following:

**Linux:**
```py
#Virtual environment (optional)
python -m venv pvenv
. pvenv/bin/activate

#Setting everything up
python -m pip install -r requirements.txt
python setup.py build_ext -i

#Running
python run.py
```

**Windows**
```py
#Virtual environment (optional)
python -m venv pvenv
"pvenv/Scripts/Activate"

#Setting everything up
python -m pip install -r requirements.txt
python setup.py build_ext -i

#Running
python run.py
```

**Mac OS**<br/>
:(
