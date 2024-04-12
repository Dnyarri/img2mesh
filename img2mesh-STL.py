#!/usr/bin/env python

'''
IMG2MESH STL - Program for conversion of image heightfield to triangle mesh in STL format
-----------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)
History:
0.1.0.0 Just started. Upper surface ok, but coordinates wrong.
0.1.0.1 Sides added. Positioning glitches investigated.
0.1.0.2 Sides and bottom added, side bug found and fixed, but sill no good solution for mirroring.
0.1.0.3 Inelegant therefore effective solution for coordinate system.
0.1.0.4 Most stupid bug fixed. Looks like ready for production.

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
__version__ = "0.1.0.4"
__maintainer__ = "Ilya Razmanov"
__email__ = "ilyarazmanov@gmail.com"
__status__ = "Development"

from tkinter import Tk
from tkinter import Label
from tkinter import filedialog
from time import time
from time import ctime

from png import Reader  # I/O with PyPNG from: https://gitlab.com/drj11/pypng

# --------------------------------------------------------------
# Creating dialog

sortir = Tk()
sortir.title('PNG to STL conversion')
sortir.geometry('+100+100')
zanyato = Label(sortir, text='Allons-y!', font=("arial", 14), padx=16, pady=10, justify='center')
zanyato.pack()
sortir.withdraw()

# Main dialog created and hidden
# --------------------------------------------------------------

# --------------------------------------------------------------
# Open source image
sourcefilename = filedialog.askopenfilename(
    title='Open source PNG file', filetypes=[('PNG', '.png')], defaultextension=('PNG', '.png')
)
if sourcefilename == '':
    quit()

source = Reader(filename=sourcefilename)  # starting PyPNG

X, Y, pixels, info = source.asDirect()  # Opening image, iDAT comes to "pixels" as bytearray, to be tuple'd later

Z = info['planes']  # Maximum CHANNEL NUMBER
imagedata = tuple((pixels))  # Attempt to fix all bytearrays into something solid

if info['bitdepth'] == 8:
    maxcolors = 255  # Maximal value for 8-bit channel
if info['bitdepth'] == 16:
    maxcolors = 65535  # Maximal value for 16-bit channel

# Open export file
resultfile = filedialog.asksaveasfile(
    mode='w',
    title='Save StereoLithography file',
    filetypes=[
        ('StereoLithography object file', '*.stl'),
        ('All Files', '*.*'),
    ],
    defaultextension=('StereoLithography object file', '.stl'),
)
if resultfile == '':
    quit()
# Both files opened
# --------------------------------------------------------------

# --------------------------------------------------------------
# Functions block:
#
# src a-la FM style src(x,y,z)
# Image should be opened as "imagedata" by main program before
# Note that X, Y, Z are not determined in function, you have to determine it in main program


def src(x, y, z):
    '''
    Analog of src from FilterMeister, force repeat edge instead of out of range
    '''
    cx = x
    cy = y
    cx = max(0, cx)
    cx = min((X - 1), cx)
    cy = max(0, cy)
    cy = min((Y - 1), cy)

    position = (cx * Z) + z  # Here is the main magic of turning two x, z into one array position
    channelvalue = int(((imagedata[cy])[position]))

    return channelvalue


# end of src function


def srcY(x, y):
    '''
    Converting to greyscale, returns Yntensity, force repeat edge instead of out of range
    '''
    cx = x
    cy = y
    cx = max(0, cx)
    cx = min((X - 1), cx)
    cy = max(0, cy)
    cy = min((Y - 1), cy)

    if info['planes'] < 3:  # supposedly L and LA
        Yntensity = src(x, y, 0)
    else:  # supposedly RGB and RGBA
        Yntensity = int(0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2))

    return Yntensity


# end of srcY function
#
# end of Functions block
# --------------------------------------------------------------

# Global positioning and scaling to tweak. Offset supposed to make everyone feeling positive, rescale supposed to scale anything to [0..1.0] regardless of what the units are

xOffset = 1.0  # To be added BEFORE rescaling to compensate 0.5 X expansion
yOffset = 1.0  # To be added BEFORE rescaling to compensate 0.5 Y expansion
zOffset = 0.0  # To be added AFTER rescaling just in case there should be something to fix

xRescale = 1.0 / (max(X, Y))
yRescale = 1.0 / (max(X, Y))
zRescale = 1.0 / maxcolors

# 	WRITING STL FILE, finally

resultfile.write('solid pryanik_nepechatnyj\n')  # opening object

# Now going to cycle through image and build mesh

for y in range(0, Y, 1):

    message = 'Processing row ' + str(y) + ' of ' + str(Y) + '...'
    sortir.deiconify()
    zanyato.config(text=message)
    sortir.update()
    sortir.update_idletasks()

    for x in range(0, X, 1):

        # Since I was unable to find clear declaration of coordinate system, I'll plug a coordinate switch here

        # Reading switch:
        xRead = x
        yRead = (Y - 1 - y)     # 'yRead = Y - y' coordinate mirror to mimic Photoshop coordinate system; +/- 1 steps below are inverted correspondingly vs. original img2mesh

        # Remains of Writing switch. No longer used since v. 0.1.0.2 but var names remained so dummy plug must be here.
        xWrite = x
        yWrite = y

        v9 = srcY(xRead, yRead)  # Current pixel to process and write. Then going to neighbours
        v1 = 0.25 * (v9 + srcY((xRead - 1), yRead) + srcY((xRead - 1), (yRead + 1)) + srcY(xRead, (yRead + 1)))  # По улитке 8-1-2
        v3 = 0.25 * (v9 + srcY(xRead, (yRead + 1)) + srcY((xRead + 1), (yRead + 1)) + srcY((xRead + 1), yRead))  # По улитке 2-3-4
        v5 = 0.25 * (v9 + srcY((xRead + 1), yRead) + srcY((xRead + 1), (yRead - 1)) + srcY(xRead, (yRead - 1)))  # По улитке 4-5-6
        v7 = 0.25 * (v9 + srcY(xRead, (yRead - 1)) + srcY((xRead - 1), (yRead - 1)) + srcY((xRead - 1), yRead))  # По улитке 6-7-8

        # finally going to pyramid building

        # top part begins
        resultfile.writelines(
            [
                f'   facet normal 0 0 1\n',  # triangle 2 normal up
                f'       outer loop\n',  # 1 - 9 - 3
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 1\n',  # triangle 4 normal up
                f'       outer loop\n',  # 3 - 9 - 5
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 1\n',  # triangle 6 normal up
                f'       outer loop\n',  # 5 - 9 - 7
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 1\n',  # triangle 8 normal up
                f'       outer loop\n',  # 7 - 9 - 1
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
            ]
        )
        # top part ends

        # left side begins
        if x == 0:
            resultfile.writelines(
                [
                    f'   facet normal -1 0 0\n',  # triangle 8- normal left
                    f'       outer loop\n',  # 1 - down1 - 7
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                    f'   facet normal -1 0 0\n',  # triangle 8- normal left
                    f'       outer loop\n',  # down1 - down7 - 7
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                ]
            )
        # left side ends

        # right side begins
        if x == (X - 1):
            resultfile.writelines(
                [
                    f'   facet normal 1 0 0\n',  # triangle 4+ normal left
                    f'       outer loop\n',  # 5 - down5 - 3
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                    f'   facet normal 1 0 0\n',  # triangle 4+ normal left
                    f'       outer loop\n',  # 3 - down5 - down3
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                ]
            )
        # right side ends

        # far side begins
        if y == 0:
            resultfile.writelines(
                [
                    f'   facet normal 0 -1 0\n',  # triangle 2- normal far
                    f'       outer loop\n',  # 3 - down - 1
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                    f'   facet normal 0 -1 0\n',  # triangle 2- normal far
                    f'       outer loop\n',  # down - down - 1
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                ]
            )
        # far side ends

        # close side begins
        if y == (Y - 1):
            resultfile.writelines(
                [
                    f'   facet normal 0 1 0\n',  # triangle 6+ normal close
                    f'       outer loop\n',  # 7 - down - 5
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                    f'   facet normal 0 1 0\n',  # triangle 6+ normal close
                    f'       outer loop\n',  # down - down - 5
                    f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                    f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                    f'       endloop\n',
                    f'   endfacet\n',
                ]
            )
        # close side ends

        # bottom part begins
        resultfile.writelines(
            [
                f'   facet normal 0 0 -1\n',  # triangle 2 normal up
                f'       outer loop\n',  # 1 - 9 - 3
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 -1\n',  # triangle 4 normal up
                f'       outer loop\n',  # 3 - 9 - 5
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 -1\n',  # triangle 6 normal up
                f'       outer loop\n',  # 5 - 9 - 7
                f'           vertex {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
                f'   facet normal 0 0 -1\n',  # triangle 8 normal up
                f'       outer loop\n',  # 7 - 9 - 1
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+0.0):e}\n',
                f'           vertex {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+0.0):e}\n',
                f'       endloop\n',
                f'   endfacet\n',
            ]
        )
        # bottom part ends

resultfile.write('endsolid pryanik_nepechatnyj')  # closing object

# Close output
resultfile.close()

# --------------------------------------------------------------
# Destroying dialog

sortir.destroy()
sortir.mainloop()

# Dialog destroyed and closed
# --------------------------------------------------------------
