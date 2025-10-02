#!/usr/bin/env python3

"""
IMG2STL - Conversion of image heightfield to triangle mesh in stereolithography STL format
-------------------------------------------------------------------------------------------

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
---------

list2stl present function for converting image-like nested X,Y,Z int lists to
3D triangle mesh height field in stereolithography STL format.

This version represents geometry variant №1, two triangles fold per four pixels,
bent according to local gradient.

This version was superseded by geometry №3 with four triangle pyramids.

This version is suspended, frozen, mothballed and encased in carbonite,
but more alive than Lenin.

Usage
------

    `list2stl.list2stl(image3d, maxcolors, result_file_name)`

where:

    `image3d` - image as list of lists of lists of int channel values;

    `maxcolors` - maximum value of int in `image3d` list;

    `result_file_name` - name of STL file to export.

References
-----------

1. `Cătălin IANCU et al., From CAD model to 3D print via “STL” file format<https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf>`_.

2. `Marshall Burns, Automated Fabrication, Section 6.5<https://www.fabbers.com/tech/STL_Format>`_.

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
__version__ = '1.22.2.2'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from math import sqrt


def list2stl(image3d, maxcolors, resultfilename):
    """Converting nested 3D list to STL heightfield triangle mesh.

    - `image3d` - image as list of lists of lists of int channel values;
    - `maxcolors` - maximum value of int in `image3d` list;
    - `resultfilename` - name of STL file to export.

    """

    Y = len(image3d)
    X = len(image3d[0])
    Z = len(image3d[0][0])

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def src(x, y, z):
        """Analog of src from FilterMeister, force repeat edge instead of out of range.
        Returns channel z value for pixel x, y.

        **WARNING:** Coordinate system mirrored against Y!"""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(Y - 1 - y)))

        channelvalue = image3d[cy][cx][z]

        return channelvalue

    def src_lum(x, y):
        """Returns brightness of pixel x, y, multiplied by opacity if exists, normalized to 0..1 range."""

        if Z == 1:  # L
            yntensity = src(x, y, 0)
        elif Z == 2:  # LA, multiply L by A. A = 0 is transparent, a = maxcolors is opaque
            yntensity = src(x, y, 0) * src(x, y, 1) / maxcolors
        elif Z == 3:  # RGB
            yntensity = 0.298936021293775 * src(x, y, 0) + 0.587043074451121 * src(x, y, 1) + 0.114020904255103 * src(x, y, 2)
        elif Z == 4:  # RGBA, multiply calculated L by A.
            yntensity = (0.298936021293775 * src(x, y, 0) + 0.587043074451121 * src(x, y, 1) + 0.114020904255103 * src(x, y, 2)) * src(x, y, 3) / maxcolors

        return yntensity / float(maxcolors)

    def normal(x1, y1, z1, x2, y2, z2, x3, y3, z3):
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

    def x_out(x, shift):
        """Recalculate source x to result x"""
        return XY_RESCALE * (x + shift + X_OFFSET)

    def y_out(y, shift):
        """Recalculate source y to result y"""
        return XY_RESCALE * (y + shift + Y_OFFSET)

    PRECISION = '6e'
    # ↑ Float output precision. Set single according to  Ref. [2]

    """ ┌────────────────────────────────────────────────────┐
        │ Mesh. STL header will be added during file writing │
        └────────────────────────────────────────────────────┘ """

    tops = []  # Top part of the object, i.e. height field.
    sides = []  # All four sides of the object.
    bottoms = []  # Bottom of the object.

    for y in range(Y - 1):
        for x in range(X - 1):
            v1 = src_lum(x, y)  # Current pixel to process and write. Then going to neighbours
            v2 = src_lum(x + 1, y)
            v3 = src_lum(x + 1, y + 1)
            v4 = src_lum(x, y + 1)

            # ↓ Finally going to build a fold!

            if abs(v1 - v3) > abs(v2 - v4):
                # Fold along 2 - 4 diagonal
                if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                    # ↓ Top triangle 1-2-4
                    tops.extend(
                        [
                            f'  facet normal {normal(x_out(x, 0), y_out(y, 0), v1, x_out(x, 1), y_out(y, 0), v2, x_out(x, 0), y_out(y, 1), v4)}\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                    # ↓ Bottom triangle 2-1-4
                    bottoms.extend(
                        [
                            '  facet normal 0 0 -1\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                    # ↓ Top triangle 4-2-3
                    tops.extend(
                        [
                            f'  facet normal {normal(x_out(x, 0), y_out(y, 1), v4, x_out(x, 1), y_out(y, 0), v2, x_out(x, 1), y_out(y, 1), v3)}\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                    # ↓ Bottom triangle 2-4-3
                    bottoms.extend(
                        [
                            '  facet normal 0 0 -1\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
            # ↑ Fold construction complete.
            else:
                # Fold along 1 - 3 diagonal
                if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                    # ↓ Top triangle 1-2-3
                    tops.extend(
                        [
                            f'  facet normal {normal(x_out(x, 0), y_out(y, 0), v1, x_out(x, 1), y_out(y, 0), v2, x_out(x, 1), y_out(y, 1), v3)}\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v2:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            '    endloop\n',
                        ]
                    )
                    # ↓ Bottom triangle 1-3-2
                    bottoms.extend(
                        [
                            '  facet normal 0 0 -1\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                if (v1 + v2 + v3 + v4) > (0.5 / maxcolors):
                    # ↓ Top triangle 1-3-4
                    tops.extend(
                        [
                            '  endfacet\n',
                            f'  facet normal {normal(x_out(x, 0), y_out(y, 0), v1, x_out(x, 1), y_out(y, 1), v3, x_out(x, 0), y_out(y, 1), v4)}\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {v1:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v3:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {v4:.{PRECISION}}\n',
                            '    endloop\n',
                            '  endfacet\n',
                        ]
                    )
                    # ↓ Bottom triangle 1-4-3
                    bottoms.extend(
                        [
                            '  facet normal 0 0 -1\n',
                            '    outer loop\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 0):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 0):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
                            f'      vertex {x_out(x, 1):.{PRECISION}} {y_out(y, 1):.{PRECISION}} {0:.{PRECISION}}\n',
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


# ↓ Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
