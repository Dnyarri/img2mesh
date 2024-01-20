# Program for conversion of image heightfield to triangle mesh
# (c) Ilya Razmanov (ilyarazmanov@gmail.com)
# History:
# 001 - Abandoned img2mesh and turned to img2mesh2 with completely different mesh structure.
# 002 - Added mesh encapsulation with cubic box to provide solid walls and bottom.
# 003 - Restructured output for easy reading, everything but globals and includes now at the end of scene.
#       Extended camera description.
# 004 - Bug with positioning found and seem to be fixed.
# 005 - Replaced Pillow I/O with PyPNG from: https://gitlab.com/drj11/pypng
#       Support for 16 bit/channel PNGs added.
# 006 - Minor output cleanup and generalization
#
#       Project mirrored at:
#       https://github.com/Dnyarri/img2mesh
#       https://gitflic.ru/project/dnyarri/img2mesh
#

import time
import png
from tkinter import filedialog

# Open source image
sourcefilename = filedialog.askopenfilename(title='Open source PNG file', filetypes=[('PNG','.png')], defaultextension = ('PNG','.png'))
if (sourcefilename == ''):
    quit()

source = png.Reader(filename = sourcefilename)  # starting PyPNG

X,Y,pixels,info = source.asDirect() # Opening image, iDAT comes to "pixels" as bytearray, to be tuple'd later

totalpixels = X*Y               # Total number OF pixels, not PIXEL NUMBER
rowlength = X*(info['planes'])  # Row length
Z = (info['planes'])            # Maximum CHANNEL NUMBER
imagedata = tuple((pixels))     # Attempt to fix all bytearrays

if (info['bitdepth'] == 8):
    maxcolors = 255             # Maximal value for 8-bit channel
if (info['bitdepth'] == 16):
    maxcolors = 65535           # Maximal value for 16-bit channel

# Open export file
resultfile = filedialog.asksaveasfile(mode='w', title='Save resulting POV file', filetypes = 
            [
			('POV-Ray scene file', '*.pov'),
            ('All Files', '*.*'),],
    defaultextension = ('POV-Ray scene file','.pov'))
if (resultfile == ''):
    quit()
# Both files opened

# src a-la FM style src(x,y,z)
# Image should be opened as "imagedata" by main program before
# Note that X, Y, Z are not determined in function, you have to determine it in main program

def src(x, y, z):  # Analog src from FM, force repeate edge instead of out of range

    cx = x; cy = y
    cx = max(0,cx); cx = min((X-1),cx)
    cy = max(0,cy); cy = min((Y-1),cy)

    position = (cx*Z) + z   # Here is the main magic of turning two x, z into one array position
    channelvalue = int(((imagedata[cy])[position]))
    
    return channelvalue
# end of src function

def srcY(x, y):  # Converting to greyscale, returns Y, force repeate edge instead of out of range

    cx = x; cy = y
    cx = max(0,cx); cx = min((X-1),cx)
    cy = max(0,cy); cy = min((Y-1),cy)

    if (info['planes'] < 3):    # supposedly L and LA
        Yntensity = src(x, y, 0)
    else:                       # supposedly RGB and RGBA
        Yntensity = int(0.2989*src(x, y, 0) + 0.587*src(x, y, 1) + 0.114*src(x, y, 2))
    
    return Yntensity
# end of srcY function

#	WRITING POV FILE

# ------------
#  POV header
# ------------

resultfile.write('// Persistence of Vision Ray Tracer Scene Description File\n')
resultfile.write('// Vers: 3.5\n')
resultfile.write('// Description: A triangle mesh file converted from image heightfield\n')
resultfile.write('// Auth: Automatically generated by img2mesh Pyton program\n')
resultfile.write('// https://github.com/Dnyarri/img2mesh\n// https://gitflic.ru/project/dnyarri/img2mesh\n')
resultfile.write('// developed by Ilya Razmanov\n// (ilyarazmanov@gmail.com)\n\n')
resultfile.write(f'// Converted from: {sourcefilename} ')
seconds = time.time()
localtime = time.ctime(seconds)
resultfile.write(f'at: {localtime}\n')
resultfile.write(f'// Source info: {info}\n\n')

#  Statements

resultfile.write('#version 3.5;\n\n')
resultfile.write('global_settings\n')
resultfile.write('{\n')
resultfile.write('  max_trace_level 3\n')
resultfile.write('  adc_bailout 0.01\n')
resultfile.write('  ambient_light <.5,.5,.5>\n')
resultfile.write('  assumed_gamma 1.0\n')
resultfile.write('}\n\n')

# Standard includes
resultfile.write('#include "colors.inc"\n\n')

# Mesh

resultfile.write('#declare thething = mesh {\n')  # Opening mesh object "thething"

# Now going to cycle through image and build mesh

for y in range(0, Y, 1):

    resultfile.write(f'\n\n // Row {y}\n')

    for x in range(0, X, 1):

        v9 = srcY(x,y)       # Current pixel to process and write. Then going to neighbours
        v1 = (v9 + srcY((x-1), y) + srcY((x-1), (y-1)) + srcY(x, (y-1)))/4.0       # По улитке 8-1-2
        v3 = (v9 + srcY(x, (y-1)) + srcY((x+1), (y-1)) + srcY((x+1), y))/4.0       # По улитке 2-3-4
        v5 = (v9 + srcY((x+1), y) + srcY((x+1), (y+1)) + srcY(x, (y+1)))/4.0       # По улитке 4-5-6
        v7 = (v9 + srcY(x, (y+1)) + srcY((x-1), (y+1)) + srcY((x-1), y))/4.0       # По улитке 6-7-8

        # going to pyramid building

        resultfile.write('\n  triangle {')    # Opening triangle 2
        resultfile.write(f'<{(x-0.5)}, {(y-0.5)}, {v1}>')
        resultfile.write(f'<{(x+0.5)}, {(y-0.5)}, {v3}>')
        resultfile.write(f'<{x}, {y}, {v9}>')
        resultfile.write('}')             # Closing triangle 2

        resultfile.write('\n  triangle {')    # Opening triangle 4
        resultfile.write(f'<{(x+0.5)}, {(y-0.5)}, {v3}>')
        resultfile.write(f'<{(x+0.5)}, {(y+0.5)}, {v5}>')
        resultfile.write(f'<{x}, {y}, {v9}>')
        resultfile.write('}')             # Closing triangle 4

        resultfile.write('\n  triangle {')    # Opening triangle 6
        resultfile.write(f'<{(x+0.5)}, {(y+0.5)}, {v5}>')
        resultfile.write(f'<{(x-0.5)}, {(y+0.5)}, {v7}>')
        resultfile.write(f'<{x}, {y}, {v9}>')
        resultfile.write('}')             # Closing triangle 6

        resultfile.write('\n  triangle {')    # Opening triangle 8
        resultfile.write(f'<{(x-0.5)}, {(y+0.5)}, {v7}>')
        resultfile.write(f'<{(x-0.5)}, {(y-0.5)}, {v1}>')
        resultfile.write(f'<{x}, {y}, {v9}>')
        resultfile.write('}')             # Closing triangle 8

resultfile.write('\n\ninside_vector <0, 0, 1>\n\n')

# Transform object to fit 1, 1, 1 cube at 0, 0, 0 coordinates
resultfile.write('\n// Object transforms to fit 1, 1, 1 cube at 0, 0, 0 coordinates\n')
resultfile.write('translate <0.5, 0.5, 0>\n')   # compensate for -0.5 extra, now object fit 0..X, 0..Y, 0..maxcolors
resultfile.write(f'translate <-0.5*{X}, -0.5*{Y}, 0>\n')  # translate to center object bottom at x = 0, y = 0, z = 0
resultfile.write(f'scale <-1.0/{max(X,Y)}, -1.0/{max(X,Y)}, 1.0/{maxcolors}>\n')  # rescale, mirroring POV coordinates to match Photoshop coordinate system

# Sample texture of textures
resultfile.write('texture {\n')
resultfile.write('  gradient z\n')
resultfile.write('  texture_map {\n')
resultfile.write('      [0.01  pigment{Red} finish{phong 1}]\n')
resultfile.write('      [0.5  pigment{Blue} finish{phong 5}]\n')
resultfile.write('      [0.99  pigment{White} finish{phong 10}]\n  }\n}\n')

resultfile.write('}\n')   # Closing mesh object "thething"

# Insert object into scene
# resultfile.write('object {thething}\n')
resultfile.write('#declare boxedthing = object {\n    intersection {\n    box {<-0.5, -0.5, 0>, <0.5, 0.5, 1.0>\n        pigment {rgb <.5, .5, 5>}\n        }\n    thething\n    }\n}\n// Constructed CGS of mesh plus bounding box thus adding side walls and bottom\n\n')
resultfile.write('object {boxedthing}\n// Finally inserting CGS into the scene\n\n')

# Camera
proportions = max(X,Y)/X
resultfile.write('#declare camera_height = 3.0;\n\n')
resultfile.write('camera {\n   // orthographic\n    location <0.0, 0.0, camera_height>\n    right x*image_width/image_height\n    up y\n    direction <0,0,1>\n    angle 2.0*(degrees(atan2(')
resultfile.write(f'{0.5 * proportions}')
resultfile.write(', camera_height-1.0))) // Supposed to fit object \n    look_at <0.0, 0.0, 0.0>\n}\n\n')

# Light
resultfile.write('light_source {0*x\n   color rgb <1,1,1>\n   translate <20, 20, 20>}\n\n')

# Close output
resultfile.close()