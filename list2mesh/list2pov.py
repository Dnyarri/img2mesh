#!/usr/bin/env python3

"""
========
list2pov
========
------------------------------------------------------------------
Conversion of image heightfield to triangle mesh in POV-Ray format
------------------------------------------------------------------

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
- ``result_file_name``: name of POV-Ray file to export.

Reference
---------

`POV-Ray`_ Documentation, Section 2.4.2.3 `Mesh`_.

.. _POV-Ray: https://www.povray.org/

.. _Mesh: https://www.povray.org/documentation/view/3.7.1/292/

-------------------
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

img2mesh Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh/tree/classic

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh?branch=classic

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2023-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.27.27.7'  # 27 Mar 2026
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from time import strftime


def list2pov(image3d, maxcolors, resultfilename):
    """Convert image (nested 3D list of ``x``, ``y``, ``z`` coordinates)
    to POV-Ray triangle mesh.

    :param image3d: image as list of lists of lists of int channel values;
    :type image3d: list[list[list[int]]
    :param int maxcolors: maximum of channel value in ``image3d`` list (int),
        255 for 8 bit and 65535 for 16 bit input;
    :param str resultfilename: name of POV file to export.

    """

    # ↓ Determining image size
    Y, X, Z = (len(image3d), len(image3d[0]), len(image3d[0][0]))

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def _pixel(x, y):
        """Getting whole pixel from image list, force repeat edge
        instead of out of range. Returns list[channel,] for pixel(x, y)."""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(y)))
        pixelvalue = image3d[cy][cx]
        return pixelvalue

    def _src_lum(x, y):
        """Returns brightness of pixel(x, y), multiplied by opacity if exists, normalized to 0..1 range."""

        if Z == 1:  # L
            l = _pixel(x, y)[0]
            return l / maxcolors
        if Z == 2:  # LA, multiply L by A. A = 0 is transparent, a = maxcolors is opaque
            l, a = _pixel(x, y)
            la = l * a / maxcolors
            return la / maxcolors
        if Z == 3:  # RGB
            r, g, b = _pixel(x, y)
            l = 0.298936021293775 * r + 0.587043074451121 * g + 0.114020904255103 * b
            return l / maxcolors
        if Z > 3:  # RGBA, multiply calculated L by A.
            r, g, b, a = _pixel(x, y)
            l = 0.298936021293775 * r + 0.587043074451121 * g + 0.114020904255103 * b
            la = l * a / maxcolors
            return la / maxcolors

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
                '  Coordinate system mimic Photoshop, i.e. the origin is top left corner.',
                '  Z axis points toward viewer.\n',
                'IMPORTANT:',
                '  Generated .pov file may be directly used as include, if the main file',
                '  contains the following:\n',
                '    #declare Main = 1;',
                '    #declare thething_transform = transform{rotate <0, 0, 0>}',
                '    #include "generated.pov"',
                '    object {thething}\n',
                ' "Main" variable in master file turns off camera, light and texture',
                '  in include file, allowing master file to take over.',
                '  Using "thething_transform" is recommended way to transform object',
                '  since it affects inside vector as well.',
                '  Remember to #declare values BEFORE #include file if you want include',
                '  to detect these values exist and stop declaring them on its own!\n\n',
                f'Source image properties:\nWidth {X} px;\nHeight {Y} px;\nColors per channel: {maxcolors + 1}\n\n',
                '  File automatically generated by',
                f'  {f"{__name__}".rpartition(".")[2]} v. {__version__} at {strftime("%d %b %Y %H:%M:%S")}',
                '  developed by Ilya Razmanov aka Ilyich the Toad',
                '    https://dnyarri.github.io',
                '    mailto:ilyarazmanov@gmail.com\n*/\n\n',
            ]
        )
    )

    """ ┌────────────────────────────┐
        │ General statements and map │
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
                '/*    Map function',
                'Maps are transfer functions z value is passed through.',
                'Result is similar to Photoshop or GIMP "Curves" applied to source image,',
                'but here map is nondestructively applied to mesh within POV-Ray.',
                'By default exported map is five points linear spline, corresponding',
                'to straight line, describing "identical" transform, i.e. input = output.',
                'You can both edit existing control points and add new ones.',
                'Note that points order is irrelevant, since POV-Ray will resort vectors',
                'according to entry value (first number in the row before comma),',
                'so you can add middle points at the end of the list below',
                'or write the whole list upside down. */\n',
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
                '      colour_map {  // Rough approximation of real terrain map height coloring',
                '        [0.0, rgb <0.2, 1.0, 0.0>]',
                '        [1.0, rgb <1.0, 0.2, 0.0>]',
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
                '        [0.0, rgbt <0, 0, 0, 1>]',
                '        [0.5 - line_width, rgbt <0, 0, 0, 1>]',
                '        [0.5 - line_width, rgbt <0, 0, 0, 0>]',
                '        [0.5, rgbt <0, 0, 0, 0>]',
                '        [0.5 + line_width, rgbt <0, 0, 0, 0>]',
                '        [0.5 + line_width, rgbt <0, 0, 0, 1>]',
                '        [1.0, rgbt <0, 0, 0, 1>]',
                '      }',
                '    }',
                '    scale 0.1',
                '  }\n',
                '#declare thething_texture_aoi =    // aoi improves curvature visualization',
                '  texture {',
                '    pigment {',
                '    aoi',
                '      colour_map {',
                '        [0.5, rgbt <0, 1, 0, 0.75>]',
                '        [1.0, rgbt <0, 1, 1, 0.75>]',
                '      }',
                '    }',
                '    finish {phong 0.0}',
                '  }\n',
                '#declare thething_texture =           // Overall texture used in the end',
                '  texture {thething_texture_bottom}',
                '  texture {thething_texture_aoi}',
                '  texture {thething_texture_top}',
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

    def _x_out(x, shift):
        """Recalculate source x to result x."""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def _y_out(y, shift):
        """Recalculate source y to result y."""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    # ↓ Float output precision. Max for Python double is supposed to be 16, however
    #   for 16-bit images 7 is enough.
    PRECISION = '7f'

    # ↓ Opening mesh object "thething"
    resultfile.write('\n#declare thething = mesh {')

    # ↓ Now going to cycle through image and build mesh

    v1 = v2 = v3 = v4 = 0.0
    # ↑ Not needed for Python but Ruff gets mad about "Undefined name" without it.

    for y in range(Y - 1):  # Mesh includes extra pixels at the right and below, therefore -1
        row = [f'\n\n  // Row {y}']  # Starting a row of folded squares.
        for x in range(X - 1):  # Mesh includes extra pixels at the right and below, therefore -1
            """ Building a folded square made of two triangles.

            Pixel order around default pixel 1:
            ┌───┬───┐
            │ 1 │ 2 │
            ├───┼───┤
            │ 4 │ 3 │
            └───┴───┘ """
            if x > 0:  # Reusing previous pixel read results
                v1 = v2
                v4 = v3
                v2 = _src_lum(x + 1, y)
                v3 = _src_lum(x + 1, y + 1)
            else:  # Start of the row, no previous pixel to reuse
                v1 = _src_lum(x, y)  # Current pixel
                v2 = _src_lum(x + 1, y)
                v3 = _src_lum(x + 1, y + 1)
                v4 = _src_lum(x, y + 1)

            pyramid = []
            if abs(v1 - v3) > abs(v2 - v4):  # Folding ⧄ along 2 ╱ 4 diagonal
                # ↓ Triangle 1-2-4 (◤ of ⧄)
                if (v1 + v2 + v4) > (0.5 / maxcolors):  # Create triangle only if there is a corner above 0
                    pyramid.extend(
                        [
                            '\n    triangle{',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v1:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v2:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v4:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            '}',
                        ]
                    )

                # ↓ Triangle 2-3-4 (◢ of ⧄)
                if (v2 + v3 + v4) > (0.5 / maxcolors):
                    pyramid.extend(
                        [
                            '\n    triangle{',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v2:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v3:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v4:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            '}',
                        ]
                    )
            else:  # Folding ⧅ along 1 ╲ 3 diagonal
                # ↓ Triangle 1-2-3 (◥ of ⧅)
                if (v1 + v2 + v3) > (0.5 / maxcolors):
                    pyramid.extend(
                        [
                            '\n    triangle{',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v1:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v2:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v3:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            '}',
                        ]
                    )

                # ↓ Triangle 1-3-4 (◣ of ⧅)
                if (v1 + v3 + v4) > (0.5 / maxcolors):
                    pyramid.extend(
                        [
                            '\n    triangle{',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v1:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v3:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            f'<{f"{_x_out(x, 0):.{PRECISION}}".rstrip("0").rstrip(".")}, {f"{_y_out(y, 1):.{PRECISION}}".rstrip("0").rstrip(".")}, Map({f"{v4:.{PRECISION}}".rstrip("0").rstrip(".")})>',
                            '}',
                        ]
                    )

            # ↓ Construction complete.
            #   Folded square completed and ready to place.
            #   AVE ME!
            row.extend(pyramid)
        # ↓ Flushing a row to file.
        resultfile.write(''.join(row))

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
    )  # ↑ Closing scene

    # ↓ Close output file
    resultfile.close()

    return None


# Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
