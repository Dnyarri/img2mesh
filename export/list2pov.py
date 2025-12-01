#!/usr/bin/env python3

"""
========
list2pov
========
------------------------------------------------------------------
Conversion of image heightfield to triangle mesh in POV-Ray format
------------------------------------------------------------------

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_
aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
--------

**list2pov** export module present function for converting images
and image-like nested lists to 3D triangle mesh height field,
and saving mesh thus obtained in `POV-Ray`_ format
according to `Mesh`_ specification.

Usage
-----

::

    list2pov.list2pov(image3d, maxcolors, result_file_name)

where:

- ``image3d``: image as list of lists of lists of int channel values;
- ``maxcolors``: maximum of channel value in ``image3d`` list (int),
255 for 8 bit and 65535 for 16 bit input;
- ``result_file_name``: name of POV-Ray file to export;
- ``threshold``: local contrast threshold (maximal difference in 2x2 pixels area),
above which geometry switch from №3 to №1.

Reference
---------

`POV-Ray`_ Documentation, Section 2.4.2.3 `Mesh`_.

.. _POV-Ray: https://www.povray.org/

.. _Mesh: https://www.povray.org/documentation/view/3.7.1/292/

-------------------
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

img2mesh Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh

"""

# History:
# --------
# 0.0.1.0   Initial standalone img2mesh version with 2x2 folding mesh, Dec 2023.
# 0.0.2.0   Switched to 1x4 pyramid mesh, Jan 2024.
# 0.0.7.0   Standalone img2mesh stable.
# 2.9.1.0   Total rewrite to remove all general transforms from POV-Ray lead to
#   rendering speed to increase more than expected.
#   Internal brightness map transfer function added.
#   Versioning set to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion
# 2.14.14.2 LAST RELEASE OF v2.
#   Rewritten from standalone img2pov to module list2pov.
#   Exported file may be used both as scene and as include.
#   Simplified mesh writing syntaxis with functions; intensity multiplication on opacity.
# 3.14.15.1 Mesh geometry completely changed to ver. 3.
# 3.19.8.1  Clipping zero or transparent pixels.
# 3.20.1.9  Since pyramid top is exactly in the middle,
# interpolation replaced with average to speed things up.
# 3.21.19.19    New mesh geometry ver. 3+, combining ver. 3 and ver. 1,
#   depending on neighbour differences threshold.
#   Threshold set ad hoc and needs more experiments.
# 3.23.13.13    All docstrings go to ReST.

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2023-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.23.13.13'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from time import strftime


def list2pov(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str, threshold: float = 0.05) -> None:
    """Convert nested 3D list of X, Y, Z coordinates to POV-Ray POV heightfield triangle mesh.

        :param image3d: image as list of lists of lists of int channel values;
        :type image3d: list[list[list[int]]
        :param int maxcolors: maximum of channel value in ``image3d`` list (int),
    255 for 8 bit and 65535 for 16 bit input;
        :param str resultfilename: name of POV file to export;
        :param float threshold: local contrast threshold (maximal difference
    in 2x2 pixels area), above which geometry switch from №3 to №1.

    """

    Y = len(image3d)
    X = len(image3d[0])
    Z = len(image3d[0][0])

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def pixel(x: int | float, y: int | float) -> list[int | float]:
        """Getting whole pixel from image list, force repeat edge instead of out of range.
        Returns list[channel,] for pixel x, y."""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(y)))

        pixelvalue = image3d[cy][cx]

        return pixelvalue

    def src(x: int | float, y: int | float, z: int) -> int | float:
        """Analog of src from FilterMeister, force repeat edge instead of out of range.
        Returns channel z value for pixel x, y."""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(y)))

        channelvalue = image3d[cy][cx][z]

        return channelvalue

    def src_lum(x: int | float, y: int | float) -> float:
        """Returns brightness of pixel x, y, multiplied by opacity if exists, normalized to 0..1 range."""

        if Z == 1:  # L
            yntensity = src(x, y, 0)
        elif Z == 2:  # LA, multiply L by A. A = 0 is transparent, a = maxcolors is opaque
            yntensity = src(x, y, 0) * src(x, y, 1) / maxcolors
        elif Z == 3:  # RGB
            r, g, b = pixel(x, y)
            yntensity = 0.298936021293775 * r + 0.587043074451121 * g + 0.114020904255103 * b
        elif Z == 4:  # RGBA, multiply calculated L by A.
            r, g, b, a = pixel(x, y)
            yntensity = (0.298936021293775 * r + 0.587043074451121 * g + 0.114020904255103 * b) * a / maxcolors

        return yntensity / float(maxcolors)

    def src_lum_blin(x: float, y: float) -> float:
        """Based on src_lum above, but returns bilinearly interpolated brightness of pixel x, y."""

        fx = float(x)  # Force float input coordinates for interpolation
        fy = float(y)

        # ↓ Neighbor pixels coordinates (square corners x0,y0; x1,y0; x0,y1; x1,y1)
        x0 = int(x)
        x1 = x0 + 1
        y0 = int(y)
        y1 = y0 + 1

        # ↓ Reading corners src_lum (see scr_lum above) and interpolating
        channelvalue = src_lum(x0, y0) * (x1 - fx) * (y1 - fy) + src_lum(x0, y1) * (x1 - fx) * (fy - y0) + src_lum(x1, y0) * (fx - x0) * (y1 - fy) + src_lum(x1, y1) * (fx - x0) * (fy - y0)

        return channelvalue

    """ ╔══════════════════╗
        ║ Writing POV file ║
        ╚══════════════════╝ """

    resultfile = open(resultfilename, 'w')

    """ ┌────────────┐
        │ POV header │
        └────────────┘ """

    resultfile.write(
        '\n'.join(
            [
                '/*',
                'Persistence of Vision Ray Tracer Scene Description File',
                'Version: 3.7',
                'Description: A triangle mesh scene file converted from image heightfield.',
                '   Coordinate system mimic Photoshop, i.e. the origin is top left corner.',
                '   Z axis points toward viewer.\n',
                'IMPORTANT:',
                '   Generated .pov file may be directly used as include, if the main file contain the following:\n',
                '       #declare Main = 1;',
                '       #declare thething_transform = transform{rotate <0, 0, 0>}',
                '       #include "generated.pov"',
                '       object {thething}\n',
                '   "Main" variable in master file turns off camera, light and texture in include file, allowing master file to take over.',
                '   Using "thething_transform" is recommended way to transform object since it affects inside vector as well.',
                '   Remember to #declare values before #include file if you want include to detect these values exist and stop declaring them on its own!\n',
                f'Source image properties: Width {X} px, Height {Y} px, Colors per channel: {maxcolors + 1}',
                'File automatically generated by',
                f'   {f"{__name__}".rpartition(".")[2]} v. {__version__} at {strftime("%d %b %Y %H:%M:%S")}',
                '   developed by Ilya Razmanov aka Ilyich the Toad',
                '       https://dnyarri.github.io',
                '       mailto:ilyarazmanov@gmail.com\n*/\n\n',
            ]
        )
    )

    """ ┌────────────────────────────┐
        │ General statements and Map │
        └────────────────────────────┘ """

    resultfile.write(
        '\n'.join(
            [
                '#version 3.7;\n',
                '#ifndef (Main)  // Include check 1\n',
                '  global_settings{',
                '    max_trace_level 3   // Set low to speed up rendering. May need to be increased for metals and glasses',
                '    adc_bailout 0.01    // Set high to speed up rendering. May need to be decreased to 1/256 for better quality',
                '    ambient_light <0.5, 0.5, 0.5>',
                '    assumed_gamma 1.0\n  }\n',
                '#end  // End include check 1\n',
                '#include "transforms.inc"\n',
                '\n/*    Map function\nMaps are transfer functions z value is passed through.\nResult is similar to Photoshop or GIMP "Curves" applied to source heightfield PNG,\nbut here map is nondestructively applied to mesh within POV-Ray.\nBy default exported map is five points linear spline, corresponding to straight line\ndescribing "identical" transform, i.e. input = output.\nYou can both edit existing control points and add new ones. Note that points order is irrelevant\nsince POV-Ray will resort vectors according to entry value (first digits in the row before comma),\nso you can add middle points at the end of the list below or write the whole list upside down. */\n',
                '#ifndef (Curve)  // Checking whether map is defined in main file',
                '  #declare Curve = function {  // Spline curve construction begins',
                '    spline { linear_spline',
                '      0.0,   <0.0,   0>,',
                '      0.25,  <0.25,  0>,',
                '      0.5,   <0.5,   0>,',
                '      0.75,  <0.75,  0>,',
                '      1.0,   <1.0,   0>}\n    };  // Construction complete',
                '#end  // End map definition check',
                '#ifndef (Map) #declare Map = function(c) {Curve(c).u}; #end  // Spline curve assigned as map\n',
            ]
        )
    )

    """ ┌───────────────────────────┐
        │ Global thething transform │
        └───────────────────────────┘ """
    resultfile.write(
        '\n'.join(
            [
                '\n/*  Global thething transform',
                'It is highly recommended to transform final boxedthing here and not in the end',
                'to keep inside vector glued to thething! */\n',
                '#ifndef (thething_transform)  // Include check',
                '  #declare thething_transform = transform{\n  // You can place your global scale, rotate etc. here\n};',
                '#end\n\n',
            ]
        )
    )

    """ ┌───────────────────────────┐
        │ Camera, light and texture │
        └───────────────────────────┘ """

    resultfile.write(
        '\n'.join(
            [
                '\n#ifndef (Main)  // Include check 2\n',
                '/*  Camera\n',
                'Coordinate system for the whole scene match Photoshop',
                'Origin is top left, z points at you */\n',
                '#declare camera_position = <0.0, 0.0, 3.0>;  // Camera position over object, used for angle\n',
                'camera {',
                '//  orthographic',
                '  location camera_position',
                '  right x*image_width/image_height',
                '  up y',
                '  sky <0, -1, 0>',
                '  direction <0, 0, vlength(camera_position - <0.0, 0.0, 1.0>)>  // May alone work for many objects. Otherwise fiddle with angle below',
                f'  angle 2.0*(degrees(atan2(0.5 * image_width * max({X}/image_width, {Y}/image_height) / {max(X, Y)}, vlength(camera_position - <0.0, 0.0, 1.0>)))) // Supposed to fit object',
                '  look_at <0.0, 0.0, 0.5>',
                '}\n',
                'light_source {<-5, -5, 5>',
                '    color rgb <1.0, 1.0, 1.0>',
                '//    area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on',
                '}',
                'light_source {<7, -3, 3>',
                '    color rgb <1.0, 1.0, 1.0>',
                '//    area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on',
                '}',
                'light_source {camera_position',
                '    color rgb <0.01, 0.01, 0.01>',
                '}',
                '\n//  Layered thething texture',
                '#declare thething_texture_bottom =    // Smooth z gradient',
                '  texture {',
                '    pigment {',
                '    gradient z',
                '      colour_map {',
                '        [0.0, rgb <1, 0, 0>]',
                '        [0.5, rgb <0, 0, 1>]',
                '        [1.0, rgb <1, 1, 1>]',
                '      }',
                '    }',
                '    finish {phong 1.0}',
                '  }\n',
                '#declare thething_texture_top =       // Sharp horizontals overlay',
                '  #declare line_width = 0.01;',
                '  texture {',
                '    pigment {',
                '    gradient z',
                '      colour_map {',
                '        [0.0, rgbt <0,0,0,1>]',
                '        [0.5 - line_width, rgbt <0,0,0,1>]',
                '        [0.5 - line_width, rgbt <0,0,0,0>]',
                '        [0.5, rgbt <0,0,0,0>]',
                '        [0.5 + line_width, rgbt <0,0,0,0>]',
                '        [0.5 + line_width, rgbt <0,0,0,1>]',
                '        [1.0, rgbt <0,0,0,1>]',
                '      }',
                '    }',
                '    scale 0.1',
                '  }\n',
                '#declare thething_texture =           // Overall texture used in the end',
                '    texture {thething_texture_bottom}',
                '    texture {thething_texture_top}',
                '\n\n#end  // End include check 2',
                '\n\n// Main mesh "thething" begins. NOW!\n',
            ]
        )
    )

    """ ┌──────┐
        │ Mesh │
        └──────┘ """

    # ↓ Global positioning and scaling to tweak.

    X_OFFSET = -0.5 * (X - 1.0)  # To be added BEFORE rescaling to center object.
    Y_OFFSET = -0.5 * (Y - 1.0)  # To be added BEFORE rescaling to center object

    XY_RESCALE = 1.0 / (max(X, Y) - 1.0)  # To fit object into 1,1,1 cube

    def x_out(x: int, shift: float) -> float:
        """Recalculate source x to result x."""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def y_out(y: int, shift: float) -> float:
        """Recalculate source y to result y."""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    # ↓ Float output precision. Max for Python double is supposed to be 16, however
    #   for 16-bit images 7 is enough.
    PRECISION = '7f'

    resultfile.write('\n#declare thething = mesh {\n')  # Opening mesh object "thething"

    # ↓ Now going to cycle through image and build mesh

    v1 = v2 = v3 = v4 = 0.0
    # ↑ Not needed for Python but Ruff gets mad about "Undefined name" without it.

    for y in range(Y - 1):  # Mesh includes extra pixels at the right and below, therefore -1
        resultfile.write(f'\n\n   // Row {y}')

        for x in range(X - 1):  # Mesh includes extra pixels at the right and below, therefore -1
            """Pixel order around default pixel 1.
            ┌───┬───┐
            │ 1 │ 2 │
            ├───┼───┤
            │ 4 │ 3 │
            └───┴───┘ """
            if x > 0:
                v1 = v2  # Reusing previous pixel read results
                v4 = v3
                v2 = src_lum(x + 1, y)
                v3 = src_lum(x + 1, y + 1)
            else:
                v1 = src_lum(x, y)  # Current pixel to process and write. Then going to neighbours
                v2 = src_lum(x + 1, y)
                v3 = src_lum(x + 1, y + 1)
                v4 = src_lum(x, y + 1)

            # ↓ Switch between geometry №1 and №3.
            #   Threshold set ad hoc and is subject to change
            if abs(v1 - v3) > threshold or abs(v2 - v4) > threshold:
                # ↓ Geometry №1, better sharp diagonals handling
                if abs(v1 - v3) > abs(v2 - v4):
                    v0 = (v2 + v4) / 2  # Fold along 2 - 4 diagonal
                else:
                    v0 = (v1 + v3) / 2  # Fold along 1 - 3 diagonal
            else:
                # ↓ Geometry №3, better for smooth areas
                v0 = (v1 + v2 + v3 + v4) / 4

            # ↓ Finally going to build a pyramid!
            #   Triangles are described clockwise.

            if (v1 + v2 + v0) > (0.5 / maxcolors):
                triangle_120 = f'\n    triangle {{<{f"{x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v1:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v2:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v0:.{PRECISION}}".rstrip("0").rstrip(".")})>}}'
                # ↑ Triangle 1-2-0
            else:
                triangle_120 = ''

            if (v0 + v2 + v3) > (0.5 / maxcolors):
                triangle_230 = f'\n    triangle {{<{f"{x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v2:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v3:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v0:.{PRECISION}}".rstrip("0").rstrip(".")})>}}'
                # ↑ Triangle 2-3-0
            else:
                triangle_230 = ''

            if (v0 + v3 + v4) > (0.5 / maxcolors):
                triangle_340 = f'\n    triangle {{<{f"{x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v3:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v4:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v0:.{PRECISION}}".rstrip("0").rstrip(".")})>}}'
                # ↑ Triangle 3-4-0
            else:
                triangle_340 = ''

            if (v0 + v1 + v4) > (0.5 / maxcolors):
                triangle_410 = f'\n    triangle {{<{f"{x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v4:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v1:.{PRECISION}}".rstrip("0").rstrip(".")})> <{f"{x_out(x, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{y_out(y, 0.5):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v0:.{PRECISION}}".rstrip("0").rstrip(".")})>}}'
                # ↑ Triangle 4-1-0
            else:
                triangle_410 = ''

            # ↓ Built triangles as four strings, now writing pyramid
            #   as single string in attempt to reduce disk access.
            resultfile.write(f'{triangle_120}{triangle_230}{triangle_340}{triangle_410}')

            # ↑ Pyramid construction complete. Ave me!

    resultfile.write(
        '\n'.join(
            [
                '\n\n  inside_vector vtransform(<0, 0, 1>, thething_transform)\n',
                f'//  clipped_by {{plane {{-z, {-1.0 / maxcolors:.{PRECISION}}}}}}  // Variant of cropping baseline at minimal color step\n',
                'transform thething_transform\n',
                '}\n//    Closed thething\n',
            ]
        )
    )  # ↑ Main object thething finished

    """ ┌────────────────────────────────────┐
        │ Inserting finished mesh into scene │
        └────────────────────────────────────┘ """

    resultfile.write(
        '\n'.join(
            [
                '\n#ifndef (Main)  // Include check 3\n',
                '#declare xy_clip = 1E-7;  // Side clipping for bounding box to remove roundoff artifacts',
                '#declare boxedthing = object {',
                '  intersection {',
                '    box {<-0.5 + xy_clip, -0.5 + xy_clip, 0>, <0.5 - xy_clip, 0.5 - xy_clip, 1.1>',
                '    // Beware of round-off errors when transforming: bounding box may hit thething!',
                '          pigment {rgb <0.5, 0.5, 5>}',
                '         transform thething_transform\n    }',
                '    object {thething texture {thething_texture}}',
                '    // Beware of round-off errors when transforming: texture may move away!',
                '  }',
                '}',
                '//    Constructed CGS "boxedthing" of mesh plus bounding box thus adding side walls and bottom\n',
                'object {boxedthing}\n',
                '\n#end  // End include check 3\n',
                '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
            ]
        )
    )  # Closing scene

    # ↓ Close output file
    resultfile.close()

    return None


# ↑ list2pov finished

# ↓ Dummy stub for standalone execution attempt
if __name__ == '__main__':
    print('Module to be imported, not run as standalone.')
