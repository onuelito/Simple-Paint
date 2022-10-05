"""
Drawing history module
"""
import src.core.canvas as canvas
import numpy as np

max_length = 20
data, index = [None]*max_length, 0

def update():
    global index, data

    #Poping first if maximum reached
    if index == max_length-1:
        data.append(None)
        data.pop(0)
        index -= 1

    if index == None: index = 0
    else: index += 1
    
    if index < max_length-1:
        for x in range(index, max_length-1):
            data[x] = None

    data[index] = np.copy(canvas.data)

def undo():
    global index, data
    if index == None or index ==0:
        print("Cannot undo: minimum index reached!"); return
    index -= 1
    canvas.data = np.copy(data[index])

def redo():
    global index
    if index == None or index+1 == max_length or data[index+1] is None:
        print("Cannot redo: maximum index reached!"); return
    index += 1
    canvas.data = np.copy(data[index])
