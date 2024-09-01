#!/usr/bin/env python3

'''
IMG2MESH - Program for conversion of image heightfield to triangle 3D-mesh in different formats
------------------------------------------------------------------------------------------------
Common GUI shell for img2pov, img2obj, img2stl and img2dxf modules.

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)  
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)  

History:
1.0.0.0 Initial production release.
2.9.1.0 DXF export added, POV export changed, multiple changes everywhere lead to whole product update.
        Versioning changed to MAINVERSION.MONTH since Jan 2024.DAY.subversion

        Main site:
        https://dnyarri.github.io

        Project mirrored at:
        https://github.com/Dnyarri/img2mesh
        https://gitflic.ru/project/dnyarri/img2mesh

'''

__author__ = "Ilya Razmanov"
__copyright__ = "(c) 2024 Ilya Razmanov"
__credits__ = "Ilya Razmanov"
__license__ = "unlicense"
__version__ = "2.9.1.0"
__maintainer__ = "Ilya Razmanov"
__email__ = "ilyarazmanov@gmail.com"
__status__ = "Production"

from tkinter import Tk
from tkinter import Label, Button, TOP, BOTTOM, X

from pathlib import Path

from img2pov import img2pov
from img2obj import img2obj
from img2stl import img2stl
from img2dxf import img2dxf

# ACHTUNG! User break definition below. Take care.
DyeDye = False  # Variable for breaking program anywhere upon conditions


def DisMiss():  # Kill dialog and continue
    global DyeDye
    DyeDye = False
    stopper.destroy()


def DyeDyeMyDarling():  # Kill dialog and kill program
    global DyeDye
    DyeDye = True
    stopper.destroy()
    quit()


# --------------------------------------------------------------
# Creating startup dialog (stopper)

iconpath = Path(__file__).resolve().parent / 'vaba.ico'
iconname = str(iconpath)
useicon = iconpath.exists()     # Check if icon file really exist. If False, it will not be used later.

stopper = Tk()
stopper.title('IMG2MESH')
if useicon:
    stopper.iconbitmap(iconname)
stopper.geometry('+200+100')
stopper.minsize(300, 360)
stopper.maxsize(500, 500)

preved01 = Label(stopper, text = 'img2mesh', font=("arial", 36), padx=16, pady=10, justify='center')
preved01.pack(side=TOP, fill=X)

preved02 = Label(stopper, text = 'PNG height fields to 3D mesh converter', font=("arial", 12), padx=16, pady=10, justify='center')
preved02.pack(side=TOP, fill=X)

butt01 = Button(stopper, text='PNG to POV...', font=('arial', 16), cursor='hand2', justify='center', command=img2pov)
butt01.pack(side=TOP, padx=4, pady=2, fill=X)

butt02 = Button(stopper, text='PNG to OBJ...', font=('arial', 16), cursor='hand2', justify='center', command=img2obj)
butt02.pack(side=TOP, padx=4, pady=2, fill=X)

butt03 = Button(stopper, text='PNG to STL...', font=('arial', 16), cursor='hand2', justify='center', command=img2stl)
butt03.pack(side=TOP, padx=4, pady=2, fill=X)

butt04 = Button(stopper, text='PNG to DXF...', font=('arial', 16), cursor='hand2', justify='center', command=img2dxf)
butt04.pack(side=TOP, padx=4, pady=2, fill=X)

butt09 = Button(
    stopper, text='Exit', font=('arial', 16), cursor='hand2', justify='center', command=DyeDyeMyDarling
)
butt09.pack(side=BOTTOM, padx=4, pady=(8, 2), fill=X)

stopper.mainloop()

# Startup dialog created, used and killed
# --------------------------------------------------------------

if DyeDye:
    quit()  # Kill program if "Exit" was pressed in stopper
