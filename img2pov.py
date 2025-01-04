#!/usr/bin/env python3

'''
IMG2POV - Program for conversion of image heightfield to triangle mesh in POVRay format
---------------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)  
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)  

History:

001         Abandoned img2mesh v.1 and turned to img2mesh v.2 with completely different mesh structure.  
005         Replaced Pillow I/O with PyPNG from: https://gitlab.com/drj11/pypng. Support for 16 bit/channel PNGs added. Added mesh encapsulation box.  
007         Output cleanup and generalization. GUI improved to show progress during long processing. Reducing unnecessary import.  
2.7.1.0     Significant code cleanup with .writelines. Versioning more clear.  
2.8.0.0     Total rewrite to remove all transforms from POVRay.  
2.8.1.0     Program converted into self-calling function to have a possibility to import it.  
2.8.2.1     Internal brightness map transfer function added. Finally it can be adjusted nondestructively within POVRay instead of re-editing in Photoshop or GIMP and re-exporting every time.  
2.8.2.5     Arbitrary decision to replace all maps with one arbitrary spline.  
2.8.3.0     Everything rewritten to fully match Photoshop coordinate system. Important changes in camera, handle with care!  
2.9.1.0     POV export changed, light and textures improved, whole product update. Versioning changed to MAINVERSION.MONTH since Jan 2024.DAY.subversion  
2.13.4.0    Exported file may be used both as scene and as include.  

-------------------
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
__version__ = "2.13.4.0"
__maintainer__ = "Ilya Razmanov"
__email__ = "ilyarazmanov@gmail.com"
__status__ = "Production"

from pathlib import Path
from time import ctime, time
from tkinter import Label, Tk, filedialog

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
    zanyato = Label(sortir, text='Starting...', font=('Courier', 12), padx=16, pady=10, justify='left')
    zanyato.pack()
    sortir.withdraw()

    # Main dialog created and hidden
    # --------------------------------------------------------------

    # Open source image
    sourcefilename = filedialog.askopenfilename(title='Open source PNG file', filetypes=[('PNG', '.png')], defaultextension=('PNG', '.png'))
    # Source file name taken

    if (sourcefilename == '') or (sourcefilename is None):
        return None
        # break if user press 'Cancel'

    source = Reader(filename=sourcefilename)
    # opening file with PyPNG

    X, Y, pixels, info = source.asDirect()
    # Opening image, iDAT comes to "pixels" generator, to be tuple'd later

    Z = info['planes']  # Maximum channel number
    imagedata = tuple(pixels)  # Building tuple from generator

    if info['bitdepth'] == 8:
        maxcolors = 255  # Maximal value for 8-bit channel
    if info['bitdepth'] == 16:
        maxcolors = 65535  # Maximal value for 16-bit channel

    # source file opened, initial data received

    # opening result file, first get name
    resultfilename = filedialog.asksaveasfilename(
        title='Save POVRay scene file',
        filetypes=[
            ('POV-Ray file', '.pov .inc'),
            ('All Files', '*.*'),
        ],
        defaultextension=('POV-Ray scene file', '.pov'),
    )

    if (resultfilename == '') or (resultfilename is None):
        return None
        # break if user press 'Cancel'

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
        cx = max(0, cx)
        cx = min((X - 1), cx)
        cy = y
        cy = max(0, cy)
        cy = min((Y - 1), cy)

        position = (cx * Z) + z  # Here is the main magic of turning two x, z into one array position
        channelvalue = int((imagedata[cy])[position])

        return channelvalue

    # end of src function

    def srcY(x, y):
        '''
        Converting to greyscale, returns Yntensity, force repeat edge instead of out of range
        '''
        cx = x
        cx = max(0, cx)
        cx = min((X - 1), cx)
        cy = y
        cy = max(0, cy)
        cy = min((Y - 1), cy)

        if info['planes'] < 3:  # supposedly L and LA
            Yntensity = src(x, y, 0)
        else:  # supposedly RGB and RGBA
            Yntensity = int(0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2))

        return Yntensity

    # end of srcY function

    # 	WRITING POV FILE

    seconds = time()
    localtime = ctime(seconds)  # will be used for debug info

    # ------------
    #  POV header
    # ---

    resultfile.writelines(
        [
            '/*\n',
            'Persistence of Vision Ray Tracer Scene Description File\n',
            'Version: 3.7\n',
            'Description: A triangle mesh scene file converted from PNG image heightfield.\n',
            '   Coordinate system mimic Photoshop, i.e. the origin is top left corner.\n',
            '   Z axis points toward viewer.\n\n',
            'IMPORTANT:\n',
            '   File may be directly used as include, if the main file contain the following:\n\n',
            '       #declare Main = 1;\n',
            '       #include "filename.inc"\n',
            '       object {thething}\n\n',
            '   "Main" variable turns off camera etc in include, allowing main file to work.\n\n',
            'Author: Automatically generated by img2mesh program\n',
            '   https://github.com/Dnyarri/img2mesh\n',
            '   https://gitflic.ru/project/dnyarri/img2mesh\n',
            'developed by Ilya Razmanov aka Ilyich the Toad\n',
            '   https://dnyarri.github.io\n',
            '   mailto:ilyarazmanov@gmail.com\n\n',
            f'Generated by: {__file__} version: {__version__} at: {localtime}\n'
            f'Converted from: {sourcefilename}\n'
            f'Source info: {info}\n'
            '*/\n\n',
        ]
    )

    #  Statements

    resultfile.writelines(
        [
            '\n',
            '#version 3.7;\n\n',
            '#ifndef (Main)  // Include check 1\n\n',
            '  global_settings{\n',
            '    max_trace_level 3   // Set low to speed up rendering. May need to be increased for metals and glasses\n',
            '    adc_bailout 0.01    // Set high to speed up rendering. May need to be decreased to 1/256 for better quality\n',
            '    ambient_light <0.5, 0.5, 0.5>\n',
            '    assumed_gamma 1.0\n  }\n\n',
            '  #include "colors.inc"\n',
            '  #include "finish.inc"\n',
            '  #include "metals.inc"\n',
            '  #include "golds.inc"\n\n',
            '#end  // End check 1\n\n',
            '\n/*    Map function\nMaps are transfer functions z value is passed through.\nResult is similar to Photoshop or GIMP "Curves" applied to source heightfield PNG,\nbut here map is nondestructively applied to mesh within POVRay.\nBy default exported map is five points linear spline, corresponding to straight line\ndescribing "identical" transform, i.e. input = output.\nYou can both edit existing control points and add new ones. Note that points order is irrelevant\nsince POVRay will resort vectors according to entry value (first digits in the row before comma),\nso you can add middle points at the end of the list below or write the whole list upside down. */\n\n',
            '#ifndef (Curve)\n',
            '  #declare Curve = function {  // Spline curve construction begins\n',
            '    spline { linear_spline\n',
            '      0.0,   <0.0,   0>\n',
            '      0.25,  <0.25,  0>\n',
            '      0.5,   <0.5,   0>\n',
            '      0.75,  <0.75,  0>\n',
            '      1.0,   <1.0,   0>}\n    }  // Construction complete\n',
            '#end\n',
            '#ifndef (map) #declare map = function(c) {Curve(c).u}; #end  // Spline curve assigned as map\n',
        ]
    )

    # Camera and light

    resultfile.writelines(
        [
            '\n#ifndef (Main)  // Include check 2\n\n',
            '/*  Camera\n\n',
            'Coordinate system for the whole scene match Photoshop\n',
            'Origin is top left, z points at you */\n\n',
            '#declare camera_position = <0.0, 0.0, 3.0>;  // Camera position over object, used for angle\n\n',
            'camera {\n',
            '  // orthographic\n',
            '  location camera_position\n',
            '  right x*image_width/image_height\n',
            '  up y\n',
            '  sky <0, -1, 0>\n',
            '  direction <0, 0, vlength(camera_position - <0.0, 0.0, 1.0>)>  // May alone work for many objects. Otherwise fiddle with angle below\n',
            f'//  angle 2.0*(degrees(atan2({0.5 * max(X,Y)/X}, vlength(camera_position - <0.0, 0.0, 1.0>)))) // Supposed to fit object\n',
            '  look_at<0.0, 0.0, 0.5>\n',
            '}\n\n',
            'light_source {0*x\n',
            '    color rgb <1.0, 1.0, 1.0>\n',
            '//    area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on\n',
            '    translate <-5, -5, 5>\n',
            '}\n',
            '\n//  Layered thething texture\n',
            '#declare thething_texture_bottom =    // Smooth z gradient\n',
            '  texture {\n',
            '    pigment {\n',
            '    gradient z\n',
            '      colour_map {\n',
            '        [0.0, rgb <1, 0, 0>]\n',
            '        [0.5, rgb <0, 0, 1>]\n',
            '        [1.0, rgb <1, 1, 1>]\n',
            '      }\n',
            '    }\n',
            '    finish {phong 1.0}\n',
            '  }\n\n',
            '#declare thething_texture_top =       // Sharp horizontals overlay\n',
            '  #declare line_width = 0.01;\n',
            '  texture {\n',
            '    pigment {\n',
            '    gradient z\n',
            '      colour_map {\n',
            '        [0.0, rgbt <0,0,0,1>]\n',
            '        [0.5 - line_width, rgbt <0,0,0,1>]\n',
            '        [0.5 - line_width, rgbt <0,0,0,0>]\n',
            '        [0.5, rgbt <0,0,0,0>]\n',
            '        [0.5 + line_width, rgbt <0,0,0,0>]\n',
            '        [0.5 + line_width, rgbt <0,0,0,1>]\n',
            '        [1.0, rgbt <0,0,0,1>]\n',
            '      }\n',
            '    }\n',
            '    scale 0.1\n',
            '  }\n\n',
            '#declare thething_texture =           // Overall texture used in the end\n',
            '    texture {thething_texture_bottom}\n',
            '    texture {thething_texture_top}\n',
            '\n\n#end // End check 2\n',
            '\n\n// Main mesh "thething" begins. NOW!\n',
        ]
    )

    # Mesh

    # Global positioning and scaling to tweak.

    xOffset = -0.5 * float(X - 1)  # To be added BEFORE rescaling to center object.
    yOffset = -0.5 * float(Y - 1)  # To be added BEFORE rescaling to center object

    yRescale = xRescale = 1.0 / float(max(X, Y))  # To fit object into 1,1,1 cube
    zRescale = 1.0 / float(maxcolors)

    resultfile.write('\n#declare thething = mesh {\n')  # Opening mesh object "thething"

    # Now going to cycle through image and build mesh

    for y in range(0, Y, 1):

        message = f'Processing row {str(y)} of {str(Y)}...'
        sortir.deiconify()
        zanyato.config(text=message)
        sortir.update()
        sortir.update_idletasks()

        resultfile.write(f'\n\n    // Row {y}\n')

        for x in range(0, X, 1):

            v9 = srcY(x, y)  # Current pixel to process and write. Then going to neighbours
            v1 = 0.25 * (v9 + srcY(x - 1, y - 1) + srcY(x, y - 1) + srcY(x - 1, y))
            v3 = 0.25 * (v9 + srcY(x, y - 1) + srcY(x + 1, y - 1) + srcY(x + 1, y))
            v5 = 0.25 * (v9 + srcY(x + 1, y) + srcY(x + 1, y + 1) + srcY(x, y + 1))
            v7 = 0.25 * (v9 + srcY(x, y + 1) + srcY(x - 1, y + 1) + srcY(x - 1, y))

            # finally going to build pyramid

            resultfile.write(
                f'\n        triangle {{<{xRescale*(x-0.5+xOffset)}, {yRescale*(y-0.5+yOffset)}, map({zRescale*v1})> <{xRescale*(x+xOffset)}, {yRescale*(y+yOffset)}, map({zRescale*v9})> <{xRescale*(x+0.5+xOffset)}, {yRescale*(y-0.5+yOffset)}, map({zRescale*v3})>}}'
            )  # Triangle 2 1-9-3

            resultfile.write(
                f'\n        triangle {{<{xRescale*(x+0.5+xOffset)}, {yRescale*(y-0.5+yOffset)}, map({zRescale*v3})> <{xRescale*(x+xOffset)}, {yRescale*(y+yOffset)}, map({zRescale*v9})> <{xRescale*(x+0.5+xOffset)}, {yRescale*(y+0.5+yOffset)}, map({zRescale*v5})>}}'
            )  # Triangle 4 3-9-5

            resultfile.write(
                f'\n        triangle {{<{xRescale*(x+0.5+xOffset)}, {yRescale*(y+0.5+yOffset)}, map({zRescale*v5})> <{xRescale*(x+xOffset)}, {yRescale*(y+yOffset)}, map({zRescale*v9})> <{xRescale*(x-0.5+xOffset)}, {yRescale*(y+0.5+yOffset)}, map({zRescale*v7})>}}'
            )  # Triangle 6 5-9-7

            resultfile.write(
                f'\n        triangle {{<{xRescale*(x-0.5+xOffset)}, {yRescale*(y+0.5+yOffset)}, map({zRescale*v7})> <{xRescale*(x+xOffset)}, {yRescale*(y+yOffset)}, map({zRescale*v9})> <{xRescale*(x-0.5+xOffset)}, {yRescale*(y-0.5+yOffset)}, map({zRescale*v1})>}}'
            )  # Triangle 8 7-9-1

        # Pyramid construction complete. Ave me!

    resultfile.writelines(
        [
            '\n\n  inside_vector <0, 0, 1>\n\n',
            f'//  clipped_by {{plane {{-z, -{zRescale}}}}}  // Variant of cropping baseline on minimal color step\n\n'
            '}\n//    Closed thething\n\n',  # Main object thething finished
            '\n#ifndef (Main)  // Include check 3\n\n',
            '#declare boxedthing = object {\n',
            '  intersection {\n',
            '    box {<-0.5, -0.5, 0>, <0.5, 0.5, 1.0>\n',
            '          pigment {rgb <0.5, 0.5, 5>}\n',
            '        }\n',
            '    object {thething texture {thething_texture}}\n',
            '  }\n',
            '}',
            '//    Constructed CGS "boxedthing" of mesh plus bounding box thus adding side walls and bottom\n\n',
            'object {boxedthing}\n\n',
            '\n#end// End check 3\n\n',
            '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
        ]
    )  # Closing solids

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
