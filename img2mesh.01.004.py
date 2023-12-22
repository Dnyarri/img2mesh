# Program for conversion of image heightfield to triangle mesh
# (c) Ilya Razmanov (ilyarazmanov@gmail.com)
# History:
# 001 - generates globals and mesh only
# 002 - added the rest of the scene (camera, light), mesh scaled to fit 1, 1, 1 cube and centered at 0, 0, 0, texture added
# 003 - squares folding according to gradient, made mesh smoother
# 004 - minor internal cleanup, 

import time
from PIL import Image
from tkinter import filedialog

# Open source image
sourcefilename = filedialog.askopenfilename(title='Open source image map', filetypes=[('PNG','.png'),('JPG','.jpg')])
if (sourcefilename == ''):
    quit()

# picture = Image.open(sourcefilename)

with Image.open(sourcefilename) as picture:
    picture.load()

# Open export file
resultfile = filedialog.asksaveasfile(mode='w', title='Save resulting POV file', filetypes = 
            [
			('POV-Ray scene file', '*.pov'),
            ('All Files', '*.*'),],
    defaultextension = ('POV-Ray scene file','.pov'))
if (resultfile == ''):
    quit()
# Both files opened

# Image properties
X,Y = picture.size
filemode = picture.mode
fileformat = picture.format

if (picture.mode == 'L'):
    Z = 1
if (picture.mode == 'LA'):
    Z = 1   # Ignoging alpha, to be changed when necessary
if (picture.mode == 'RGB'):
    Z = 3
if (picture.mode == 'RGBA'):
    Z = 3   # Ignoging alpha, to be changed when necessary

if (picture.mode != 'L'):
    picture = picture.convert('L')  # Forced conversion to L, skipping A, to be changed when necessary

def src(x, y):  # Analog src from FM, force repeate edge instead of out of range

    if (x < 0):
        x = 0
    if (x > X):
        x = X
    if (y < 0):
        y = 0
    if (y > Y):
        y = Y
    
    channel = picture.getpixel((x,y))
    return channel

#	WRITING POV FILE

# ------------
#  POV header
# ------------

resultfile.write('// Persistence of Vision Ray Tracer Scene Description File\n')
resultfile.write('// Vers: 3.5\n')
resultfile.write('// Description: A mesh file converted from mage heightfield\n')
resultfile.write('// Auth: Automatically generated by img2mesh Pyton program\n')
resultfile.write('// made by Ilya Razmanov.\n\n\n')
resultfile.write(f'//Converted from: {sourcefilename} ')
seconds = time.time()
localtime = time.ctime(seconds)
resultfile.write(f'at:{localtime}\n')
resultfile.write(f'//Source format: {fileformat} Converted to: {picture.format}   Source mode: {filemode} Converted to: {picture.mode}    Image size: {picture.size}\n\n')

#  Statements

resultfile.write('#version 3.5;\n\n')
resultfile.write('global_settings\n')
resultfile.write('{\n')
resultfile.write('  max_trace_level 3\n')
resultfile.write('  adc_bailout 0.01\n')
resultfile.write('  ambient_light <.5,.5,.5>\n')
resultfile.write('  assumed_gamma 1.0\n')
resultfile.write('}\n\n')

# Camera
resultfile.write('camera {  location <0.0, 0.0, 3.0>\n   look_at <0.0, 0.0, 0.0>\n    right x*image_width/image_height\n}\n\n')

# Light
resultfile.write('light_source {0*x\n   color rgb <1,1,1>\n   translate <20, 20, 20>}\n\n')

# Standard includes
resultfile.write('#include "colors.inc"\n\n')

# Mesh

resultfile.write('#declare thething = mesh {\n')  # Opening mesh object "thething"

# Now going to cycle through image and build mesh

compensation = 0.5  # Offset to compensate for 2 increments in reading cycles

# FUNNY FINDING: With offset smaller than 0.5 it creates sparse mesh, that is incorrect tracing but may be used for special effects

for y in range(0, Y, 2):

    for x in range(0, X, 2):

        v1 = src(x, y)       # Я пиксели считаю по улитке
        v2 = src((x+1), y)
        v3 = src((x+1), (y+1))
        v4 = src(x, (y+1))   # Курсант Жаба перебор пикселей закончил

        if (abs(v1-v3) < abs(v2-v4)):

            resultfile.write('  triangle {')              # Opening triangle top-left
            resultfile.write(f'<{x - compensation*x}, {y - compensation*y}, {v1}>, <{x+1 - compensation*x}, {y - compensation*y}, {v2}>, <{x - compensation*x}, {y+1 - compensation*y}, {v4}>')   # triangle 1-2-4
            resultfile.write('}\n')                       # Closing triangle

            resultfile.write('  triangle {')              # Opening triangle bottom-right
            resultfile.write(f'<{x+1 - compensation*x}, {y - compensation*y}, {v2}>, <{x+1 - compensation*x}, {y+1 - compensation*y}, {v3}>, <{x - compensation*x}, {y+1 - compensation*y}, {v4}>')   # triangle 2-3-4
            resultfile.write('}\n')                       # Closing triangle

        else:

            resultfile.write('  triangle {')              # Opening triangle top-right
            resultfile.write(f'<{x - compensation*x}, {y - compensation*y}, {v1}>, <{x+1 - compensation*x}, {y - compensation*y}, {v2}>, <{x+1 - compensation*x}, {y+1 - compensation*y}, {v3}>')   # triangle 1-2-3
            resultfile.write('}\n')                       # Closing triangle

            resultfile.write('  triangle {')              # Opening triangle bototm-left
            resultfile.write(f'<{x - compensation*x}, {y - compensation*y}, {v1}>, <{x - compensation*x}, {y+1 - compensation*y}, {v4}>, <{x+1 - compensation*x}, {y+1 - compensation*y}, {v3}>')   # triangle 1-4-3
            resultfile.write('}\n')                       # Closing triangle


resultfile.write('inside_vector <0, 0, 1>\n\n')

# Resize object to fit 1, 1, 1 cube at 0, 0, 0 coordinates
resultfile.write('// Object transforms to fit 1, 1, 1 cube at 0, 0, 0 coordinates\n')
resultfile.write(f'scale <-2.000000/{max(X,Y)}, -2.000000/{max(X,Y)}, 1.000000/255.000000>\n')
resultfile.write('translate <0.5, 0.5, 0>\n\n')

# Sample texture of textures
resultfile.write('texture {\n')
resultfile.write('  gradient z\n')
resultfile.write('  texture_map {\n')
resultfile.write('      [0.01  pigment{Red} finish{phong 1}]\n')
resultfile.write('      [0.5  pigment{Blue} finish{phong 5}]\n')
resultfile.write('      [0.99  pigment{White} finish{phong 10}]\n  }\n}\n')

resultfile.write('}\n')   # Closing mesh object "thething"

# Insert object into scene
resultfile.write('object {thething}\n')

# Close output
resultfile.close()