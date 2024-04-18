#!/usr/bin/env python

'''
IMG2OBJ - Program for conversion of image heightfield to triangle mesh in OBJ format
-----------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)
History:
1.0.0.0 Initial production release.
1.0.1.0 Program converted into self-calling function to have a possibility to import it.

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
__version__ = "1.0.1.0"
__maintainer__ = "Ilya Razmanov"
__email__ = "ilyarazmanov@gmail.com"
__status__ = "Production"

from tkinter import Tk
from tkinter import Label
from tkinter import filedialog

from pathlib import Path

from png import Reader  # I/O with PyPNG from: https://gitlab.com/drj11/pypng

# ACHTUNG! Starting a whole-program procedure!

def img2obj():
    '''
    Procedure for opening PNG heightfield and creating Wavefront .obj 3D mesh file from it.

    '''

    # --------------------------------------------------------------
    # Creating dialog

    iconpath = Path(__file__).resolve().parent / 'vaba.ico'
    iconname = str(iconpath)
    useicon = iconpath.exists()     # Check if icon file really exist. If False, it will not be used later.

    sortir = Tk()
    sortir.title('PNG to OBJ conversion')
    if useicon:
        sortir.iconbitmap(iconname) # Replacement for simple sortir.iconbitmap('name.ico') - ugly but stable.
    sortir.geometry('+200+100')
    zanyato = Label(sortir, text='Allons-y!', font=("arial", 14), padx=16, pady=10, justify='center')
    zanyato.pack()
    sortir.withdraw()

    # Main dialog created and hidden
    # --------------------------------------------------------------


    # Open source image
    sourcefilename = filedialog.askopenfilename(
        title='Open source PNG file', filetypes=[('PNG', '.png')], defaultextension=('PNG', '.png')
    )
    # Source file name taken

    if (sourcefilename == '') or (sourcefilename == None):
        return None
        # break if user press 'Cancel'

    source = Reader(filename=sourcefilename)
    # opening file with PyPNG

    X, Y, pixels, info = source.asDirect()
    # Opening image, iDAT comes to "pixels" as bytearray, to be tuple'd later

    Z = info['planes']          # Maximum CHANNEL NUMBER
    imagedata = tuple((pixels)) # Attempt to fix all bytearrays

    if info['bitdepth'] == 8:
        maxcolors = 255         # Maximal value for 8-bit channel
    if info['bitdepth'] == 16:
        maxcolors = 65535       # Maximal value for 16-bit channel

    # source file opened, initial data received

    # opening result file, first get name
    resultfilename = filedialog.asksaveasfilename(
        title='Save Wavefront OBJ file',
        filetypes=[
            ('Wavefront OBJ file', '*.obj'),
            ('All Files', '*.*'),
        ],
        defaultextension=('Wavefront OBJ file', '.obj'),
    )

    if (resultfilename == '') or (sourcefilename == None):
        return None
        # break if user press 'Cancel'
    # return doesn't seem to work well with .asksaveasfile

    resultfile = open(resultfilename, 'w')
    # result file opened

    # Both files opened

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
    
    # end of Functions block
    # --------------------------------------------------------------

    # Global positioning and scaling to tweak.

    xOffset = -0.5*float(X-1)  # To be added BEFORE rescaling to center object.
    yOffset = -0.5*float(Y-1)  # To be added BEFORE rescaling to center object
    zOffset = 0.0

    xRescale = 1.0 / float(max(X, Y))    # To fit object into 1,1,1 cube
    yRescale = xRescale
    zRescale = 1.0 / float(maxcolors)

    # 	WRITING OBJ FILE, finally

    resultfile.write('o pryanik_nepechatnyj\n')  # opening object

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
            v1 = 0.25 * (v9 + srcY((xRead - 1), yRead) + srcY((xRead - 1), (yRead + 1)) + srcY(xRead, (yRead + 1)))
            v3 = 0.25 * (v9 + srcY(xRead, (yRead + 1)) + srcY((xRead + 1), (yRead + 1)) + srcY((xRead + 1), yRead))
            v5 = 0.25 * (v9 + srcY((xRead + 1), yRead) + srcY((xRead + 1), (yRead - 1)) + srcY(xRead, (yRead - 1)))
            v7 = 0.25 * (v9 + srcY(xRead, (yRead - 1)) + srcY((xRead - 1), (yRead - 1)) + srcY((xRead - 1), yRead))

            # finally going to pyramid building

            # top part begins
            resultfile.writelines(
                [
                    f'v {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                    f'v {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                    f'v {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                    'f -3 -2 -1\n',     # triangle 2

                    f'v {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v3):e}\n',
                    f'v {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                    f'v {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                    'f -3 -2 -1\n',     # triangle 4

                    f'v {(xRescale*(xWrite+0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v5):e}\n',
                    f'v {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                    f'v {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                    f'f -3 -2 -1\n',     # triangle 6

                    f'v {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite+0.5+yOffset)):e} {(zOffset+zRescale*v7):e}\n',
                    f'v {(xRescale*(xWrite+xOffset)):e} {(yRescale*(yWrite+yOffset)):e} {(zOffset+zRescale*v9):e}\n',
                    f'v {(xRescale*(xWrite-0.5+xOffset)):e} {(yRescale*(yWrite-0.5+yOffset)):e} {(zOffset+zRescale*v1):e}\n',
                    f'f -3 -2 -1\n',     # triangle 8
                ]
            )
            # top part ends

    resultfile.write('# end pryanik_nepechatnyj')  # closing object

    # Close output
    resultfile.close()

    # --------------------------------------------------------------
    # Destroying dialog

    sortir.destroy()
    sortir.mainloop()

    # Dialog destroyed and closed
    # --------------------------------------------------------------

# Procedure ended, the program begins
if __name__ == "__main__":
    img2obj()