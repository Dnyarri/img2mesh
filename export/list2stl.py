#!/usr/bin/env python3

"""
========
list2stl
========
--------------------------------------------------------------------------------
Conversion of image heightfield to triangle mesh in stereolithography STL format
--------------------------------------------------------------------------------

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_
aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
--------

**list2stl** export module present function for converting images
and image-like nested lists to 3D triangle mesh height field,
and saving mesh thus obtained in stereolithography `STL`_ format.

Usage
-----

::

    list2stl.list2stl(image3d, maxcolors, result_file_name)

where:

- ``image3d``: image as list of lists of lists of int channel values;
- ``maxcolors``: maximum of channel value in ``image3d`` list (int),
255 for 8 bit and 65535 for 16 bit input;
- ``result_file_name``: name of POV-Ray file to export;
- ``threshold``: local contrast threshold (maximal difference in 2x2 pixels area),
above which geometry switch from №3 to №1.

References
----------

1. `Cătălin IANCU et al.`_, From CAD model to 3D print via “STL” file format.

2. `Marshall Burns, Automated Fabrication, Section 6.5`_.

3. `STL`_ (STereoLithography) File Format, ASCII. Sustainability of Digital Formats: Planning for Library of Congress Collections.

.. _Cătălin IANCU et al.: https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf

.. _Marshall Burns, Automated Fabrication, Section 6.5: https://www.fabbers.com/tech/STL_Format

.. _STL: https://www.loc.gov/preservation/digital/formats/fdd/fdd000506.shtml

-------------------
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

img2mesh Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh

"""

# History
# -------
# 1.0.0.0   Initial production release.
# 1.9.1.0   Multiple changes.
#   Versioning changed to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion
# 1.13.4.0  Rewritten from standalone img2stl to module list2stl.
# 3.14.16.1 Mesh geometry completely changed to ver. 3.
# 3.18.22.2 Normals improved. Fixed confluent triangles along sides.
# 3.19.8.1  Clipping zero or transparent pixels.
# 3.20.1.9  Since pyramid top is exactly in the middle,
#   interpolation replaced with average to speed things up.
# 3.21.19.19    New mesh geometry ver. 3+, combining ver. 3 and ver. 1,
#   depending on neighbour differences threshold.
#   Threshold set ad hoc and needs more experiments.
# 3.23.13.13    All docstrings go to ReST.

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.23.13.13'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from math import sqrt


def list2stl(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str, threshold: float = 0.05) -> None:
    """Converting nested 3D list to STL heightfield triangle mesh.

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

    def normal(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, x3: float, y3: float, z3: float) -> str:
        """Normal calculation"""

        nx = ((y2 - y1) * (z3 - z1)) - ((y3 - y1) * (z2 - z1))
        ny = ((z2 - z1) * (x3 - x1)) - ((x2 - x1) * (z3 - z1))
        nz = ((x2 - x1) * (y3 - y1)) - ((x3 - x1) * (y2 - y1))

        length = sqrt((nx * nx) + (ny * ny) + (nz * nz))
        # ↑ Pythagoras, in a good sense of this word

        return f'{nx / length:.{PRECISION}} {ny / length:.{PRECISION}} {nz / length:.{PRECISION}}'
        # ↑ Output as space separated string since it's the simplest format for further use

    """ ╔══════════════════╗
        ║ Writing STL file ║
        ╚══════════════════╝ """

    # ↓ Global positioning and scaling to tweak.
    #   Offset supposed to make everyone feeling positive, rescale supposed to scale anything
    #   to [0..1.0] regardless of what the units are.

    X_OFFSET = Y_OFFSET = 1.0

    XY_RESCALE = 1.0 / (max(X, Y) - 1.0)  # To fit object into 1,1,1 cube

    def x_out(x: int, shift: float) -> float:
        """Recalculate source x to result x"""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def y_out(y: int, shift: float) -> float:
        """Recalculate source y to result y"""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    # ↓ Float output precision. Set single according to  Ref. [2]
    PRECISION = '6e'

    """ ┌────────────────────────────────────────────────────┐
        │ Mesh. STL header will be added during file writing │
        └────────────────────────────────────────────────────┘ """

    tops = []  # Top part of the object, i.e. height field.
    sides = []  # All four sides of the object.
    bottoms = []  # Bottom of the object.

    v1 = v2 = v3 = v4 = 0.0
    # ↑ Not needed for Python but Ruff gets mad about "Undefined name" without it.

    for y in range(Y - 1):
        for x in range(X - 1):
            if x > 0:
                v1 = v2
                v4 = v3
                v2 = src_lum(x + 1, y)
                v3 = src_lum(x + 1, y + 1)
            else:
                v1 = src_lum(x, y)
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
                # ↓ Fix for cases when only one corner is > 0
                if v0 == 0:
                    v0 = (v1 + v2 + v3 + v4) / 4
            else:
                # ↓ Geometry №3, better for smooth areas
                v0 = (v1 + v2 + v3 + v4) / 4

            # ↓ Finally going to build a pyramid!
            #   Triangles are described counterclockwise.

            if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                # ↓ top part 1-2-0
                tops.extend(
                    [
                        f'  facet normal {normal(x_out(x, 0), y_out(y, 0), v1, x_out(x, 1), y_out(y, 0), v2, x_out(x, 0.5), y_out(y, 0.5), v0)}\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {v0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
                # ↓ bottom part 2-1-0
                bottoms.extend(
                    [
                        '  facet normal 0 0 -1\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
            if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                # ↓ top part 2-3-0
                tops.extend(
                    [
                        f'  facet normal {normal(x_out(x, 1), y_out(y, 0), v2, x_out(x, 1), y_out(y, 1), v3, x_out(x, 0.5), y_out(y, 0.5), v0)}\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {v0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
                # ↓ bottom part 3-2-0
                bottoms.extend(
                    [
                        '  facet normal 0 0 -1\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
            if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                # ↓ top part 3-4-0
                tops.extend(
                    [
                        f'  facet normal {normal(x_out(x, 1), y_out(y, 1), v3, x_out(x, 0), y_out(y, 1), v4, x_out(x, 0.5), y_out(y, 0.5), v0)}\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {v0:.{PRECISION}}\n',
                        '    endloop\n',
                    ]
                )
                # ↓ bottom part 4-3-0
                bottoms.extend(
                    [
                        '  facet normal 0 0 -1\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
            if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                # ↓ top part 4-1-0
                tops.extend(
                    [
                        '  endfacet\n',
                        f'  facet normal {normal(x_out(x, 0), y_out(y, 1), v4, x_out(x, 0), y_out(y, 0), v1, x_out(x, 0.5), y_out(y, 0.5), v0)}\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {v0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
                # ↓ bottom part 1-4-0
                bottoms.extend(
                    [
                        '  facet normal 0 0 -1\n',
                        '    outer loop\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                        f'      vertex {x_out(x, 0.5):.{PRECISION}} {y_out(y, 0.5):.{PRECISION}} {0:.{PRECISION}}\n',
                        '    endloop\n',
                        '  endfacet\n',
                    ]
                )
                # ↑ tops and bottoms ends

            # ↓ left side begins
            if x == 0:
                if v1 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal -1 0 0\n',
                            '    outer loop\n',  # 1 - down 1b - 4b
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if v4 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal -1 0 0\n',
                            '    outer loop\n',  # 4b - up 4 - 1
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
            # ↑ left side ends

            # ↓ right side begins
            if x == (X - 2):
                if v3 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 1 0 0\n',
                            '    outer loop\n',  # 3 - down 3b - 2b
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if v2 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 1 0 0\n',
                            '    outer loop\n',  # 2b - up 2 - 3
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
            # ↑ right side ends

            # ↓ far side begins
            if y == 0:
                if v2 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 0 -1 0\n',
                            '    outer loop\n',  # 2 - down 2b - 1b
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if v1 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 0 -1 0\n',
                            '    outer loop\n',  # 1b - 1 - 2
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
            # ↑ far side ends

            # ↓ close side begins
            if y == (Y - 2):
                if v4 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 0 1 0\n',
                            '    outer loop\n',  # 4 - down 4b - 3b
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if v3 > (0.5 / maxcolors):  # Blocking confluent triangles where two points match
                    sides.extend(
                        [
                            '  facet normal 0 1 0\n',
                            '    outer loop\n',  # 3b - up 3 - 4
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
            # ↑ close side ends

    # ↓ Combining all lists to file
    #   Joining to str gives ca. 3x writing speed vs. writelines,
    #   but too big a str will take much memory, therefore
    #   writing is implemented by chunks, taking into account that
    #   one facet takes 7 lines. On my system speedup effect kicks in
    #   at chunk_size = 280 and stabilize at chunk_size = 560.
    #   chunk_size = 700 equals to 25 pyramids.
    chunk_size = 700
    with open(resultfilename, 'w') as resultfile:
        resultfile.write('solid pryanik_nepechatnyj\n')  # STL file header
        for i in range(0, len(bottoms), chunk_size):
            resultfile.write(''.join(bottoms[i : i + chunk_size]))
        for i in range(0, len(sides), chunk_size):
            resultfile.write(''.join(sides[i : i + chunk_size]))
        for i in range(0, len(tops), chunk_size):
            resultfile.write(''.join(tops[i : i + chunk_size]))
        resultfile.write('endsolid pryanik_nepechatnyj')  # STL file closing

    return None


# ↑ list2stl finished

# ↓ Dummy stub for standalone execution attempt
if __name__ == '__main__':
    print('Module to be imported, not run as standalone.')
