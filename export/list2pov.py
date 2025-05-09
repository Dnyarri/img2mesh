#!/usr/bin/env python3

"""
IMG2POV - Conversion of image heightfield to triangle mesh in POV-Ray format
-----------------------------------------------------------------------------

Created by: `Ilya Razmanov <mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
---------

`list2pov` present function for converting image-like nested X,Y,Z int lists to
3D triangle mesh height field in POV-Ray format.

Usage
------

    `list2pov.list2pov(image3d, maxcolors, result_file_name)`

where:

    `image3d`: image as list of lists of lists of int channel values;

    `maxcolors`: maximum value of int in `image3d` list;

    `result_file_name`: name of POV-Ray file to export.

Reference
----------

`POV-Ray Documentation, Section 2.4.2.3 Mesh<https://www.povray.org/documentation/view/3.7.1/292/>`_.

History
--------

0.0.1.0     Initial standalone img2mesh version with 2x2 folding mesh, Dec 2023.

0.0.2.0     Switched to 1x4 pyramid mesh, Jan 2024.

0.0.7.0     Standalone img2mesh stable.

2.9.1.0     Total rewrite to remove all transforms from POV-Ray.
Internal brightness map transfer function added;
finally it can be adjusted nondestructively within POV-Ray instead of re-editing
in Photoshop or GIMP and re-exporting every time.
Versioning set to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion

2.14.14.2   LAST RELEASE OF v2.
Rewritten from standalone img2pov to module list2pov.
Exported file may be used both as scene and as include.
Simplified mesh writing syntaxis with functions; intensity multiplication on opacity.

3.14.15.1   Mesh geometry completely changed.

-------------------
Main site: `The Toad's Slimy Mudhole <https://dnyarri.github.io>`_

Git repositories:
`Main at Github<https://github.com/Dnyarri/img2mesh>`_; `Gitflic mirror<https://gitflic.ru/project/dnyarri/img2mesh>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2023-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.17.9.12'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from time import ctime, time


def list2pov(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str) -> None:
    """Convert nested 3D list of X, Y, Z coordinates to POV heightfield triangle mesh.

    `image3d`: image as list of lists of lists of int channel values;

    `maxcolors`: maximum value of int in `image3d` list;

    `resultfilename`: name of POV-Ray file to export.

    """

    # Determining list sizes
    Y = len(image3d)
    X = len(image3d[0])
    Z = len(image3d[0][0])

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def src(x: int | float, y: int | float, z: int) -> int | float:
        """
        Analog of src from FilterMeister, force repeat edge instead of out of range.
        Returns channel z value for pixel x, y

        """

        cx = int(x)
        cy = int(y)  # nearest neighbor for float input
        cx = max(0, cx)
        cx = min((X - 1), cx)
        cy = max(0, cy)
        cy = min((Y - 1), cy)

        channelvalue = image3d[cy][cx][z]

        return channelvalue

    def src_lum(x: int | float, y: int | float) -> float:
        """Returns brightness of pixel x, y, multiplied on opacity if exists, normalized to 0..1 range."""

        if Z == 1:  # L
            yntensity = src(x, y, 0)
        elif Z == 2:  # LA, multiply L on A. A = 0 is transparent, a = maxcolors is opaque
            yntensity = src(x, y, 0) * src(x, y, 1) / maxcolors
        elif Z == 3:  # RGB
            yntensity = 0.298936021293775 * src(x, y, 0) + 0.587043074451121 * src(x, y, 1) + 0.114020904255103 * src(x, y, 2)
        elif Z == 4:  # RGBA, multiply calculated L on A.
            yntensity = (0.298936021293775 * src(x, y, 0) + 0.587043074451121 * src(x, y, 1) + 0.114020904255103 * src(x, y, 2)) * src(x, y, 3) / maxcolors

        return yntensity / float(maxcolors)

    def src_lum_blin(x: float, y: float) -> float:
        """Based on src_lum above, but returns bilinearly interpolated brightness of pixel x, y"""

        fx = float(x)  # Force float input coordinates for interpolation
        fy = float(y)

        # Neighbor pixels coordinates (square corners x0,y0; x1,y0; x0,y1; x1,y1)
        x0 = int(x)
        x1 = x0 + 1
        y0 = int(y)
        y1 = y0 + 1

        # Reading corners src_lum (see scr_lum above) and interpolating
        channelvalue = src_lum(x0, y0) * (x1 - fx) * (y1 - fy) + src_lum(x0, y1) * (x1 - fx) * (fy - y0) + src_lum(x1, y0) * (fx - x0) * (y1 - fy) + src_lum(x1, y1) * (fx - x0) * (fy - y0)

        return channelvalue

    """ ╔══════════════════╗
        ║ Writing POV file ║
        ╚══════════════════╝ """

    resultfile = open(resultfilename, 'w')

    localtime = ctime(time())  # will be used for debug info

    """ ┌────────────┐
        │ POV header │
        └────────────┘ """

    resultfile.writelines(
        [
            '/*\n',
            'Persistence of Vision Ray Tracer Scene Description File\n',
            'Version: 3.7\n',
            'Description: A triangle mesh scene file converted from image heightfield.\n',
            '   Coordinate system mimic Photoshop, i.e. the origin is top left corner.\n',
            '   Z axis points toward viewer.\n\n',
            'IMPORTANT:\n',
            '   Generated .pov file may be directly used as include, if the main file contain the following:\n\n',
            '       #declare Main = 1;\n',
            '       #declare thething_transform = transform{rotate <0, 0, 0>}\n',
            '       #include "generated.pov"\n',
            '       object {thething}\n\n',
            '   "Main" variable in master file turns off camera, light and texture in include file, allowing master file to take over.\n',
            '   Using "thething_transform" is recommended way to transform object since it affects inside vector as well.\n',
            '   Remember to #declare values before #include file if you want include to detect these values exist and stop declaring them on its own!\n\n',
            f'Source image properties: Width {X} px, Height {Y} px, Colors per channel: {maxcolors}\n',
            f'File automatically generated at {localtime} by {__name__} module ver. {__version__}\n',
            'developed by Ilya Razmanov aka Ilyich the Toad\n',
            '   https://dnyarri.github.io\n',
            '   mailto:ilyarazmanov@gmail.com\n*/\n\n',
        ]
    )

    """ ┌────────────────────────────┐
        │ General statements and map │
        └────────────────────────────┘ """

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
            '#end  // End include check 1\n\n',
            '#include "transforms.inc"\n\n',
            '\n/*    Map function\nMaps are transfer functions z value is passed through.\nResult is similar to Photoshop or GIMP "Curves" applied to source heightfield PNG,\nbut here map is nondestructively applied to mesh within POV-Ray.\nBy default exported map is five points linear spline, corresponding to straight line\ndescribing "identical" transform, i.e. input = output.\nYou can both edit existing control points and add new ones. Note that points order is irrelevant\nsince POV-Ray will resort vectors according to entry value (first digits in the row before comma),\nso you can add middle points at the end of the list below or write the whole list upside down. */\n\n',
            '#ifndef (Curve)  // Checking whether map is defined in main file\n',
            '  #declare Curve = function {  // Spline curve construction begins\n',
            '    spline { linear_spline\n',
            '      0.0,   <0.0,   0>,\n',
            '      0.25,  <0.25,  0>,\n',
            '      0.5,   <0.5,   0>,\n',
            '      0.75,  <0.75,  0>,\n',
            '      1.0,   <1.0,   0>}\n    };  // Construction complete\n',
            '#end  // End map definition check\n',
            '#ifndef (map) #declare map = function(c) {Curve(c).u}; #end  // Spline curve assigned as map\n',
        ]
    )

    """ ┌───────────────────────────┐
        │ Global thething transform │
        └───────────────────────────┘ """
    resultfile.writelines(
        [
            '\n/*  Global thething transform\n',
            'It is highly recommended to transform final boxedthing here and not in the end\n',
            'to keep inside vector glued to thething! */\n\n',
            '#ifndef (thething_transform)  // Include check\n',
            '  #declare thething_transform = transform{rotate <0, 0, 0>};  // Put your transforms here\n',
            '#end\n\n',
        ]
    )

    """ ┌───────────────────────────┐
        │ Camera, light and texture │
        └───────────────────────────┘ """

    resultfile.writelines(
        [
            '\n#ifndef (Main)  // Include check 2\n\n',
            '/*  Camera\n\n',
            'Coordinate system for the whole scene match Photoshop\n',
            'Origin is top left, z points at you */\n\n',
            '#declare camera_position = <0.0, 0.0, 3.0>;  // Camera position over object, used for angle\n\n',
            'camera {\n',
            '//  orthographic\n',
            '  location camera_position\n',
            '  right x*image_width/image_height\n',
            '  up y\n',
            '  sky <0, -1, 0>\n',
            '  direction <0, 0, vlength(camera_position - <0.0, 0.0, 1.0>)>  // May alone work for many objects. Otherwise fiddle with angle below\n',
            f'  angle 2.0*(degrees(atan2(0.5 * image_width * max({X}/image_width, {Y}/image_height) / {max(X, Y)}, vlength(camera_position - <0.0, 0.0, 1.0>)))) // Supposed to fit object\n',
            '  look_at <0.0, 0.0, 0.5>\n',
            '}\n\n',
            'light_source {<-5, -5, 5>\n',
            '    color rgb <1.0, 1.0, 1.0>\n',
            '//    area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on\n',
            '}\n',
            'light_source {<7, -3, 3>\n',
            '    color rgb <1.0, 1.0, 1.0>\n',
            '//    area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on\n',
            '}\n',
            'light_source {camera_position\n',
            '    color rgb <0.01, 0.01, 0.01>\n',
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
            '\n\n#end  // End include check 2\n',
            '\n\n// Main mesh "thething" begins. NOW!\n',
        ]
    )

    """ ┌──────┐
        │ Mesh │
        └──────┘ """

    # Global positioning and scaling to tweak.

    X_OFFSET = -0.5 * (X - 1.0)  # To be added BEFORE rescaling to center object.
    Y_OFFSET = -0.5 * (Y - 1.0)  # To be added BEFORE rescaling to center object

    XY_RESCALE = 1.0 / (max(X, Y) - 1.0)  # To fit object into 1,1,1 cube

    def x_out(x: int, shift: float) -> float:
        """Recalculate source x to result x"""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def y_out(y: int, shift: float) -> float:
        """Recalculate source y to result y"""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    resultfile.write('\n#declare thething = mesh {\n')  # Opening mesh object "thething"

    # Now going to cycle through image and build mesh

    precision = '6f'
    # Float output precision. Max for Python double is supposed to be 16, however
    # for 16-bit images 6 should be enough.

    for y in range(Y - 1):  # Mesh includes extra pixels at the right and below, therefore -1
        resultfile.write(f'\n\n   // Row {y}\n')

        for x in range(X - 1):  # Mesh includes extra pixels at the right and below, therefore -1
            """Pixel order around default pixel 1.
            ┌───┬───┐
            │ 1 │ 2 │
            ├───┼───┤
            │ 4 │ 3 │
            └───┴───┘
            """
            v1 = src_lum(x, y)  # Current pixel to process and write. Then going to neighbours
            v2 = src_lum(x + 1, y)
            v3 = src_lum(x + 1, y + 1)
            v4 = src_lum(x, y + 1)
            v0 = src_lum_blin(x + 0.5, y + 0.5)  # Center of the pyramid

            # Finally going to build a pyramid!
            # Triangles are described clockwise.

            resultfile.write(
                f'\n    triangle {{<{x_out(x, 0):.{precision}}, {y_out(y, 0):.{precision}}, map({v1:.{precision}})> <{x_out(x, 1):.{precision}}, {y_out(y, 0):.{precision}}, map({v2:.{precision}})> <{x_out(x, 0.5):.{precision}}, {y_out(y, 0.5):.{precision}}, map({v0:.{precision}})>}}'
            )  # Triangle 1-2-0

            resultfile.write(
                f'\n    triangle {{<{x_out(x, 1):.{precision}}, {y_out(y, 0):.{precision}}, map({v2:.{precision}})> <{x_out(x, 1):.{precision}}, {y_out(y, 1):.{precision}}, map({v3:.{precision}})> <{x_out(x, 0.5):.{precision}}, {y_out(y, 0.5):.{precision}}, map({v0:.{precision}})>}}'
            )  # Triangle 2-3-0

            resultfile.write(
                f'\n    triangle {{<{x_out(x, 1):.{precision}}, {y_out(y, 1):.{precision}}, map({v3:.{precision}})> <{x_out(x, 0):.{precision}}, {y_out(y, 1):.{precision}}, map({v4:.{precision}})> <{x_out(x, 0.5):.{precision}}, {y_out(y, 0.5):.{precision}}, map({v0:.{precision}})>}}'
            )  # Triangle 3-4-0

            resultfile.write(
                f'\n    triangle {{<{x_out(x, 0):.{precision}}, {y_out(y, 1):.{precision}}, map({v4:.{precision}})> <{x_out(x, 0):.{precision}}, {y_out(y, 0):.{precision}}, map({v1:.{precision}})> <{x_out(x, 0.5):.{precision}}, {y_out(y, 0.5):.{precision}}, map({v0:.{precision}})>}}'
            )  # Triangle 4-1-0

            # Pyramid construction complete. Ave me!

    resultfile.writelines(
        [
            '\n\n  inside_vector vtransform(<0, 0, 1>, thething_transform)\n\n',
            f'//  clipped_by {{plane {{-z, {-1.0 / maxcolors:.{precision}}}}}}  // Variant of cropping baseline on minimal color step\n\n',
            'transform thething_transform\n\n',
            '}\n//    Closed thething\n\n',
        ]
    )  # Main object thething finished

    """ ┌────────────────────────────────────┐
        │ Inserting finished mesh into scene │
        └────────────────────────────────────┘ """

    resultfile.writelines(
        [
            '\n#ifndef (Main)  // Include check 3\n\n',
            '#declare boxedthing = object {\n',
            '  intersection {\n',
            '    box {<-0.5+1E-7, -0.5+1E-7, 0>, <0.5-1E-7, 0.5-1E-7, 1.1>\n',
            '    // Beware of round-off errors when transforming: bounding box may hit thething!\n',
            '          pigment {rgb <0.5, 0.5, 5>}\n',
            '         transform thething_transform\n    }\n',
            '    object {thething texture {thething_texture}}\n',
            '    // Beware of round-off errors when transforming: texture may move away!\n',
            '  }\n',
            '}\n',
            '//    Constructed CGS "boxedthing" of mesh plus bounding box thus adding side walls and bottom\n\n',
            'object {boxedthing}\n\n',
            '\n#end  // End include check 3\n\n',
            '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
        ]
    )  # Closing scene

    # Close output file
    resultfile.close()

    return None


# Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
