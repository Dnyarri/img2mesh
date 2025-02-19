#!/usr/bin/env python3

"""
IMG2OBJ - Conversion of image heightfield to triangle mesh in Wavefront OBJ format
-----------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com) aka Ilyich the Toad (mailto:amphisoft@gmail.com)

Overview
---------

list2obj present function for converting image-like nested X,Y,Z int lists to 3D triangle mesh height field in Wavefront OBJ format.

Usage
------

`list2obj.list2obj(image3d, maxcolors, result_file_name)`

where:

`image3d` - image as list of lists of lists of int channel values;

`maxcolors` - maximum value of int in `image3d` list;

`result_file_name` - name of OBJ file to export.

Reference
----------

https://paulbourke.net/dataformats/obj/obj_spec.pdf

History
--------

1.0.0.0     Initial production release.

1.9.1.0     Multiple changes lead to whole product update. Versioning changed to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion

1.13.4.0    Rewritten from standalone img2obj to module list2obj.

3.14.15.1   Mesh geometry completely changed.

-------------------
Main site:
https://dnyarri.github.io

Git repository:
https://github.com/Dnyarri/img2mesh; mirror: https://gitflic.ru/project/dnyarri/img2mesh

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.14.19.10'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'


def list2obj(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str) -> None:
    """Converting nested 3D list to Wavefront OBJ heightfield triangle mesh.

    `image3d` - image as list of lists of lists of int channel values.

    `maxcolors` - maximum value of int in `image3d` list.

    `resultfilename` - name of OBJ file to export.

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
        Returns channel z value for pixel x, y.

        **WARNING:** Coordinate system mirrored against Y!

        """

        cx = int(x)
        cy = int(Y - 1 - y)  # Mirroring from Photoshop to Wavefront
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
            yntensity = 0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2)
        elif Z == 4:  # RGBA, multiply calculated L on A. A = 0 is transparent, a = maxcolors is opaque
            yntensity = (0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2)) * src(x, y, 3) / maxcolors

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
        ║ Writing OBJ file ║
        ╚══════════════════╝ """

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

    resultfile = open(resultfilename, 'w')

    """ ┌────────────┐
        │ OBJ header │
        └────────────┘ """
    resultfile.write(f'# Generated by: {__name__} {__version__}\n')

    resultfile.write('o pryanik_nepechatnyj\n')  # opening object

    """ ┌──────┐
        │ Mesh │
        └──────┘ """

    for y in range(0, Y - 1, 1):
        for x in range(0, X - 1, 1):
            v1 = src_lum(x, y)  # Current pixel to process and write. Then going to neighbours
            v2 = src_lum(x + 1, y)
            v3 = src_lum(x + 1, y + 1)
            v4 = src_lum(x, y + 1)
            v0 = src_lum_blin(x + 0.5, y + 0.5)  # Center of the pyramid

            # Finally going to build a pyramid!

            resultfile.writelines(
                [
                    f'v {x_out(x, 0)} {y_out(y, 0)} {v1}\n',
                    f'v {x_out(x, 1)} {y_out(y, 0)} {v2}\n',
                    f'v {x_out(x, 0.5)} {y_out(y, 0.5)} {v0}\n',
                    'f -2 -3 -1\n',
                    # triangle 1-2-0, order changed to counterclocwise that means normal up
                    f'v {x_out(x, 1)} {y_out(y, 0)} {v2}\n',
                    f'v {x_out(x, 1)} {y_out(y, 1)} {v3}\n',
                    f'v {x_out(x, 0.5)} {y_out(y, 0.5)} {v0}\n',
                    'f -2 -3 -1\n',  # triangle 2-3-0
                    f'v {x_out(x, 1)} {y_out(y, 1)} {v3}\n',
                    f'v {x_out(x, 0)} {y_out(y, 1)} {v4}\n',
                    f'v {x_out(x, 0.5)} {y_out(y, 0.5)} {v0}\n',
                    'f -2 -3 -1\n',  # triangle 3-4-0
                    f'v {x_out(x, 0)} {y_out(y, 1)} {v4}\n',
                    f'v {x_out(x, 0)} {y_out(y, 0)} {v1}\n',
                    f'v {x_out(x, 0.5)} {y_out(y, 0.5)} {v0}\n',
                    'f -2 -3 -1\n',  # triangle 4-1-0
                ]
            )  # Pyramid construction complete. Ave me!

    resultfile.write('# end pryanik_nepechatnyj')  # closing object

    # Close output
    resultfile.close()

    return None


# Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
