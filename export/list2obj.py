#!/usr/bin/env python3

"""
IMG2OBJ - Conversion of image heightfield to triangle mesh in Wavefront OBJ format
-----------------------------------------------------------------------------------

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
---------

list2obj present function for converting image-like nested X,Y,Z int lists to
3D triangle mesh height field in Wavefront OBJ format.

Usage
------

    `list2obj.list2obj(image3d, maxcolors, result_file_name)`

where:

    `image3d` - image as list of lists of lists of int channel values;

    `maxcolors` - maximum value of int in `image3d` list;

    `result_file_name` - name of OBJ file to export.

Reference
----------

`B1. Object Files (.obj)<https://paulbourke.net/dataformats/obj/obj_spec.pdf>`_.

History
--------

1.0.0.0     Initial production release.

1.9.1.0     Multiple changes lead to whole product update.
Versioning changed to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion

1.13.4.0    Rewritten from standalone img2obj to module list2obj.

3.14.15.1   Mesh geometry completely changed to ver. 3.

3.19.8.1    Clipping zero or transparent pixels.

3.20.1.9    Since pyramid top is exactly in the middle,
interpolation replaced with average to speed things up.

3.21.19.19  New mesh geometry ver. 3+, combining ver. 3 and ver. 1,
depending on neighbour differences threshold.
Threshold set ad hoc and needs more experiments.

-------------------
Main site: `The Toad's Slimy Mudhole <https://dnyarri.github.io>`_

Git repositories:
`Main at Github <https://github.com/Dnyarri/img2mesh>`_;
`Gitflic mirror <https://gitflic.ru/project/dnyarri/img2mesh>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.21.21.21'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from time import strftime

def list2obj(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str, threshold: float = 0.05) -> None:
    """Converting nested 3D list to Wavefront OBJ heightfield triangle mesh.

    - `image3d` - image as list of lists of lists of int channel values;
    - `maxcolors` - maximum value of int in `image3d` list;
    - `resultfilename` - name of OBJ file to export.

    """

    Y = len(image3d)
    X = len(image3d[0])
    Z = len(image3d[0][0])

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def pixel(x: int | float, y: int | float) -> list[int | float]:
        """Getting whole pixel from image list, force repeat edge instead of out of range.
        Returns list[channel,] for pixel x, y.

        **WARNING:** Coordinate system mirrored against Y!"""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(Y - 1 - y)))

        pixelvalue = image3d[cy][cx]

        return pixelvalue

    def src(x: int | float, y: int | float, z: int) -> int | float:
        """Analog of src from FilterMeister, force repeat edge instead of out of range.
        Returns channel z value for pixel x, y.

        **WARNING:** Coordinate system mirrored against Y!"""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(Y - 1 - y)))

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
        ║ Writing OBJ file ║
        ╚══════════════════╝ """

    # ↓ Global positioning and scaling to tweak.

    X_OFFSET = -0.5 * (X - 1.0)  # To be added BEFORE rescaling to center object.
    Y_OFFSET = -0.5 * (Y - 1.0)  # To be added BEFORE rescaling to center object

    XY_RESCALE = 1.0 / (max(X, Y) - 1.0)  # To fit object into 1,1,1 cube

    def x_out(x: int, shift: float) -> float:
        """Recalculate source x to result x"""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def y_out(y: int, shift: float) -> float:
        """Recalculate source y to result y"""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    # ↓ Float output precision. Max for Python double is supposed to be 16, however
    #   for 16-bit images 7 is enough.
    PRECISION = '7f'

    resultfile = open(resultfilename, 'w')

    """ ┌────────────┐
        │ OBJ header │
        └────────────┘ """
    resultfile.write(f'# Generated by {f'{__name__}'.rpartition('.')[2]} v. {__version__} at {strftime('%d %b %Y %H:%M:%S')}\n')

    resultfile.write('o pryanik_nepechatnyj\n')  # opening object

    """ ┌──────┐
        │ Mesh │
        └──────┘ """

    for y in range(Y - 1):
        for x in range(X - 1):
            if x == 0:
                v1 = src_lum(x, y)  # Current pixel to process and write. Then going to neighbours
                v2 = src_lum(x + 1, y)
                v3 = src_lum(x + 1, y + 1)
                v4 = src_lum(x, y + 1)
            else:
                v1 = v2
                v4 = v3
                v2 = src_lum(x + 1, y)
                v3 = src_lum(x + 1, y + 1)

            # ↓ Switch between geometry №1 and №3.
            #   Threshold set ad hoc and is subject to change
            if abs(v1 - v3) > threshold or abs(v2 - v4) > threshold:
                if abs(v1 - v3) > abs(v2 - v4):
                    v0 = (v2 + v4) / 2
                else:
                    v0 = (v1 + v3) / 2
            else:
                v0 = (v1 + v2 + v3 + v4) / 4

            # ↓ Finally going to build a pyramid!
            #   Triangles are described clockwise, then connection order reset counterclockwise.
            if (v1 + v2 + v0) > (0.5 / maxcolors):
                resultfile.writelines(
                    [
                        f'v {f'{x_out(x, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v1:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v2:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v0:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        'f -2 -3 -1\n',
                    ]
                )  # ↑ triangle 1-2-0, order changed to counterclockwise that means normal up
            if (v0 + v2 + v3) > (0.5 / maxcolors):
                resultfile.writelines(
                    [
                        f'v {f'{x_out(x, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v2:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v3:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v0:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        'f -2 -3 -1\n',
                    ]
                )  # ↑ triangle 2-3-0, order changed to counterclockwise
            if (v0 + v3 + v4) > (0.5 / maxcolors):
                resultfile.writelines(
                    [
                        f'v {f'{x_out(x, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v3:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v4:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v0:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        'f -2 -3 -1\n',
                    ]
                )  # ↑ triangle 3-4-0, order changed to counterclockwise
            if (v0 + v1 + v4) > (0.5 / maxcolors):
                resultfile.writelines(
                    [
                        f'v {f'{x_out(x, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 1):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v4:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v1:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        f'v {f'{x_out(x, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{y_out(y, 0.5):.{PRECISION}}'.rstrip('0').rstrip('.')} {f'{v0:.{PRECISION}}'.rstrip('0').rstrip('.')}\n',
                        'f -2 -3 -1\n',
                    ]
                )  # ↑ triangle 4-1-0, order changed to counterclockwise
            # ↑ Pyramid construction complete. Ave me!

    resultfile.write('# end pryanik_nepechatnyj')  # closing object

    # ↓ Close output
    resultfile.close()

    return None
# ↑ list2obj finished

# ↓ Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
