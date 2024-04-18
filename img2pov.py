#!/usr/bin/env python

'''
IMG2POV - Program for conversion of image heightfield to triangle mesh in POVRay format
---------------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)
History:

001     Abandoned img2mesh v.1 and turned to img2mesh v.2 with completely different mesh structure.
005     Replaced Pillow I/O with PyPNG from: https://gitlab.com/drj11/pypng
        Support for 16 bit/channel PNGs added. Added mesh encapsulation box.
        Extended POVRay camera description.
        Restructured output for easy reading.
007     Output cleanup and generalization. GUI improved to show progress during long processing.
        Reducing unnecessary import.
2.7.1.0 Significant code cleanup with .writelines. Versioning more clear.
2.8.0.0 Total rewrite to remove all transforms from POVRay.
2.8.1.0 Program converted into self-calling function to have a possibility to import it.

        Main site:
        https://dnyarri.github.io

        Project mirrored at:
        https://github.com/Dnyarri/img2mesh
        https://gitflic.ru/project/dnyarri/img2mesh

'''

__author__ = "Ilya Razmanov"
__copyright__ = "(c) 2023-2024 Ilya Razmanov"
__credits__ = "Ilya Razmanov"
__license__ = "unlicense"
__version__ = "2.8.1.0"
__maintainer__ = "Ilya Razmanov"
__email__ = "ilyarazmanov@gmail.com"
__status__ = "Production"

from tkinter import Tk
from tkinter import Label
from tkinter import filedialog

from time import time
from time import ctime

from pathlib import Path

from png import Reader  # I/O with PyPNG from: https://gitlab.com/drj11/pypng

# ACHTUNG! Starting a whole-program procedure!


def img2pov():
    '''
    Procedure for opening PNG heightfield and creating POVRay .pov 3D mesh file from it.

    '''

    # --------------------------------------------------------------
    # Creating dialog

    iconpath = Path(__file__).resolve().parent / 'vaba.ico'
    iconname = str(iconpath)
    useicon = iconpath.exists()  # Check if icon file really exist. If False, it will not be used later.

    sortir = Tk()
    sortir.title('PNG to POV conversion')
    if useicon:
        sortir.iconbitmap(iconname)  # Replacement for simple sortir.iconbitmap('name.ico') - ugly but stable.
    sortir.geometry('+200+100')
    zanyato = Label(sortir, text='Starting...', font=("arial", 14), padx=16, pady=10, justify='center')
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
        title='Save POVRay scene file',
        filetypes=[
            ('POV-Ray scene file', '*.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension=('POV-Ray scene file', '.pov'),
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
        Analog src from FM, force repeat edge instead of out of range
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

    # 	WRITING POV FILE

    # ------------
    #  POV header
    # ---

    resultfile.writelines(
        [
            '/*\n',
            'Persistence of Vision Ray Tracer Scene Description File\n',
            'Version: 3.7\n',
            'Description: A triangle mesh scene file converted from image heightfield\n',
            'Author: Automatically generated by img2mesh program\n',
            '   https://github.com/Dnyarri/img2mesh\n',
            '   https://gitflic.ru/project/dnyarri/img2mesh\n',
            'developed by Ilya Razmanov aka Ilyich the Toad\n',
            '   https://dnyarri.github.io/\n',
            '   mailto:ilyarazmanov@gmail.com\n',
            '*/\n\n',
        ]
    )

    resultfile.write(f'//    Converted from: {sourcefilename} ')
    seconds = time()
    localtime = ctime(seconds)
    resultfile.write(f'at: {localtime}\n//    Source info: {info}\n\n')

    #  Statements

    resultfile.writelines(
        [
            '\n',
            '#version 3.7;\n\n',
            'global_settings{\n',
            '    max_trace_level 3   // Set low to speed up rendering. May need to be increased for metals and glasses\n',
            '    adc_bailout 0.01    // Set high to speed up rendering. May need to be decreased to 1/256 for better quality\n',
            '    ambient_light <0.5,0.5,0.5>\n',
            '    assumed_gamma 1.0\n}\n\n',
            '#include "colors.inc"\n',
            '#include "finish.inc"\n',
            '#include "metals.inc"\n',
            '#include "golds.inc"\n\n',
            '#declare thethingtexturebottom =\n',
            '    texture {\n',
            '        pigment {\n',
            '        gradient z\n',
            '            colour_map {\n',
            '                [0.0,  Red]\n',
            '                [0.5, Blue]\n',
            '                [1.0,  White]\n',
            '            }\n',
            '        }\n',
            '    finish {phong 1.0}\n',
            '    }\n',
            '\n',
            '#declare thethingtexturetop =\n',
            '    texture {\n',
            '        pigment {\n',
            '        gradient z\n',
            '        colour_map {\n',
            '            [0.00, rgbt <0,0,0,1>]\n',
            '            [0.48, rgbt <0,0,0,1>]\n',
            '            [0.50, rgbt <0,0,0,0>]\n',
            '            [0.52, rgbt <0,0,0,1>]\n',
            '            [1.00, rgbt <0,0,0,1>]\n',
            '        }\n',
            '      }\n',
            '      scale 0.2\n',
            '    }\n',
        ]
    )

    # Mesh

    # Global positioning and scaling to tweak.

    xOffset = -0.5 * float(X - 1)  # To be added BEFORE rescaling to center object.
    yOffset = -0.5 * float(Y - 1)  # To be added BEFORE rescaling to center object
    zOffset = 0.0

    xRescale = 1.0 / float(max(X, Y))  # To fit object into 1,1,1 cube
    yRescale = xRescale
    zRescale = 1.0 / float(maxcolors)

    resultfile.write('\n\n#declare thething = mesh {\n')  # Opening mesh object "thething"

    # Now going to cycle through image and build mesh

    for y in range(0, Y, 1):

        message = 'Processing row ' + str(y) + ' of ' + str(Y) + '...'
        sortir.deiconify()
        zanyato.config(text=message)
        sortir.update()
        sortir.update_idletasks()

        resultfile.write(f'\n\n    // Row {y}\n')

        for x in range(0, X, 1):

            # Reading switch:
            xRead = X - 1 - x
            yRead = Y - 1 - y

            # Last remains of writing switch. No longer used but var names remained active so dummy plug must be here.
            xWrite = x
            yWrite = y

            v9 = srcY(xRead, yRead)  # Current pixel to process and write. Then going to neighbours
            v1 = 0.25 * (v9 + srcY((xRead + 1), yRead) + srcY((xRead + 1), (yRead + 1)) + srcY(xRead, (yRead + 1)))
            v3 = 0.25 * (v9 + srcY(xRead, (yRead + 1)) + srcY((xRead - 1), (yRead + 1)) + srcY((xRead - 1), yRead))
            v5 = 0.25 * (v9 + srcY((xRead - 1), yRead) + srcY((xRead - 1), (yRead - 1)) + srcY(xRead, (yRead - 1)))
            v7 = 0.25 * (v9 + srcY(xRead, (yRead - 1)) + srcY((xRead + 1), (yRead - 1)) + srcY((xRead + 1), yRead))

            # finally going to pyramid building

            resultfile.write(
                f'\n        triangle{{<{xRescale*(xWrite-0.5+xOffset)}, {yRescale*(yWrite-0.5+yOffset)}, {zRescale*v1}> <{xRescale*(xWrite+xOffset)}, {yRescale*(yWrite+yOffset)}, {zRescale*v9}> <{xRescale*(xWrite+0.5+xOffset)}, {yRescale*(yWrite-0.5+yOffset)}, {zRescale*v3}>}}'
            )  # Triangle 2 1-9-3

            resultfile.write(
                f'\n        triangle{{<{xRescale*(xWrite+0.5+xOffset)}, {yRescale*(yWrite-0.5+yOffset)}, {zRescale*v3}> <{xRescale*(xWrite+xOffset)}, {yRescale*(yWrite+yOffset)}, {zRescale*v9}> <{xRescale*(xWrite+0.5+xOffset)}, {yRescale*(yWrite+0.5+yOffset)}, {zRescale*v5}>}}'
            )  # Triangle 4 3-9-5

            resultfile.write(
                f'\n        triangle{{<{xRescale*(xWrite+0.5+xOffset)}, {yRescale*(yWrite+0.5+yOffset)}, {zRescale*v5}> <{xRescale*(xWrite+xOffset)}, {yRescale*(yWrite+yOffset)}, {zRescale*v9}> <{xRescale*(xWrite-0.5+xOffset)}, {yRescale*(yWrite+0.5+yOffset)}, {zRescale*v7}>}}'
            )  # Triangle 6 5-9-7

            resultfile.write(
                f'\n        triangle{{<{xRescale*(xWrite-0.5+xOffset)}, {yRescale*(yWrite+0.5+yOffset)}, {zRescale*v7}> <{xRescale*(xWrite+xOffset)}, {yRescale*(yWrite+yOffset)}, {zRescale*v9}> <{xRescale*(xWrite-0.5+xOffset)}, {yRescale*(yWrite-0.5+yOffset)}, {zRescale*v1}>}}'
            )  # Triangle 8 7-9-1

            # completed pyramid. Ave me!

    resultfile.write('\n\n  inside_vector <0, 0, 1>\n\n')

    # Sample texture of textures
    resultfile.writelines(
        [
            '  texture{thethingtexturebottom}\n',
            '  texture{thethingtexturetop}\n',
            '}\n//    Closed thething\n\n',
            '#declare boxedthing = object{\n',
            '    intersection {\n',
            '    box {<-0.5, -0.5, 0>, <0.5, 0.5, 1.0>\n',
            '        pigment {rgb <0.5, 0.5, 5>}\n',
            '        }\n',
            '    thething\n',
            '    }\n',
            '}',
            '//    Constructed CGS "boxedthing" of mesh plus bounding box thus adding side walls and bottom\n\n',
            'object{boxedthing}\n\n',
        ]
    )  # Closing solids

    # Camera
    proportions = max(X, Y) / X
    resultfile.writelines(
        [
            '#declare camera_height = 3.0;\n\n',
            'camera{\n',
            '//    orthographic\n',
            '    location <0.0, 0.0, camera_height>\n',
            '    right x*image_width/image_height\n' '    up y\n' '    direction <0, 0, 1>\n',
            f'    angle 2.0*(degrees(atan2({0.5 * proportions}, camera_height-1.0)))    // Supposed to fit object\n',
            '    look_at <0.0, 0.0, 0.0>\n}\n\n',
        ]
    )

    # Light
    resultfile.write('light_source{0*x\n    color rgb <1.0, 1.0, 1.0>\n    translate <20, 20, 20>\n}\n')
    resultfile.write('\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/')
    # Close output
    resultfile.close()

    # --------------------------------------------------------------
    # Destroying dialog

    sortir.destroy()
    sortir.mainloop()

    # Dialog destroyed and closed
    # --------------------------------------------------------------

    return None


# Procedure ended, the program begins
if __name__ == "__main__":
    img2pov()
