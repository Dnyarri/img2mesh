#!/usr/bin/env python3

"""
IMG2STL - Conversion of image heightfield to triangle mesh in stereolithography STL format
-------------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com) aka Ilyich the Toad (mailto:amphisoft@gmail.com)

Overview:
----------

list2stl present function for converting image-like nested X,Y,Z int lists to 3D triangle mesh height field in stereolithography STL format.

Usage:
-------

`list2stl.list2stl(image3d, maxcolors, result_file_name)`

where:

`image3d` - image as list of lists of lists of int channel values.

`maxcolors` - maximum value of int in `image3d` list.

`result_file_name` - name of STL file to export.

History:
---------

1.0.0.0     Initial production release.

1.9.1.0     Multiple changes. Versioning changed to MAINVERSION.MONTH_since_Jan_2024.DAY.subversion

1.13.4.0    Rewritten from standalone img2stl to module list2stl.

-------------------
Main site:
https://dnyarri.github.io

Project mirrored at:
https://github.com/Dnyarri/img2mesh; https://gitflic.ru/project/dnyarri/img2mesh

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.14.1.1'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'


def list2stl(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str) -> None:
    """Converting nested 3D list to STL heightfield triangle mesh.

    `image3d` - image as list of lists of lists of int channel values.

    `maxcolors` - maximum value of int in `image3d` list.

    `resultfilename` - name of STL file to export.

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
        Returns int channel z value for pixel x, y

        """

        cx = int(x)
        cy = int(y)  # nearest neighbor for float input
        cx = max(0, cx)
        cx = min((X - 1), cx)
        cy = max(0, cy)
        cy = min((Y - 1), cy)

        channelvalue = image3d[cy][cx][z]

        return channelvalue

    # end of src function

    def src_lum(x: int | float, y: int | float) -> int | float:
        """
        Returns brightness of pixel x, y

        """

        if Z < 3:  # supposedly L and LA
            yntensity = src(x, y, 0)
        else:  # supposedly RGB and RGBA
            yntensity = int(0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2))

        return yntensity

    # end of src_lum function

    """ ╔══════════════════╗
        ║ Writing STL file ║
        ╚══════════════════╝ """

    # Global positioning and scaling to tweak. Offset supposed to make everyone feeling positive, rescale supposed to scale anything to [0..1.0] regardless of what the units are

    xOffset = 1.0  # To be added BEFORE rescaling to compensate 0.5 X expansion
    yOffset = 1.0  # To be added BEFORE rescaling to compensate 0.5 Y expansion
    zOffset = 0.0  # To be added AFTER rescaling just in case there should be something to fix

    yRescale = xRescale = 1.0 / float(max(X, Y))  # To fit object into 1,1,1 cube
    zRescale = 1.0 / float(maxcolors)

    resultfile = open(resultfilename, 'w')

    """ ┌────────────┐
        │ STL header │
        └────────────┘ """

    resultfile.write('solid pryanik_nepechatnyj\n')  # opening object

    """ ┌──────┐
        │ Mesh │
        └──────┘ """

    for y in range(0, Y, 1):
        for x in range(0, X, 1):
            # Since I was unable to find clear declaration of coordinate system, I'll plug a coordinate switch here

            # Reading switch:
            xRead = x
            yRead = Y - 1 - y
            # 'yRead = Y - y' coordinate mirror to mimic Photoshop coordinate system; +/- 1 steps below are inverted correspondingly vs. original img2mesh

            # Remains of Writing switch. No longer used since v. 0.1.0.2 but var names remained so dummy plug must be here.
            xWrite = x
            yWrite = y

            """Pyramid structure around default pixel 9.
            Remember yRead = Y - 1 - y
            ┌───┬───┬───┐
            │ 1 │   │ 3 │
            ├───┼───┼───┤
            │   │ 9 │   │
            ├───┼───┼───┤
            │ 7 │   │ 5 │
            └───┴───┴───┘
            """
            v9 = src_lum(xRead, yRead)  # Current pixel to process and write. Then going to neighbours
            v1 = 0.25 * (v9 + src_lum((xRead - 1), yRead) + src_lum((xRead - 1), (yRead + 1)) + src_lum(xRead, (yRead + 1)))
            v3 = 0.25 * (v9 + src_lum(xRead, (yRead + 1)) + src_lum((xRead + 1), (yRead + 1)) + src_lum((xRead + 1), yRead))
            v5 = 0.25 * (v9 + src_lum((xRead + 1), yRead) + src_lum((xRead + 1), (yRead - 1)) + src_lum(xRead, (yRead - 1)))
            v7 = 0.25 * (v9 + src_lum(xRead, (yRead - 1)) + src_lum((xRead - 1), (yRead - 1)) + src_lum((xRead - 1), yRead))

            # finally going to pyramid building

            # top part begins
            resultfile.writelines(
                [
                    '   facet normal 0 0 1\n',  # triangle 2 normal up
                    '       outer loop\n',  # 1 - 9 - 3
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v1):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + zRescale * v9):e}\n',
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v3):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 1\n',  # triangle 4 normal up
                    '       outer loop\n',  # 3 - 9 - 5
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v3):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + zRescale * v9):e}\n',
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v5):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 1\n',  # triangle 6 normal up
                    '       outer loop\n',  # 5 - 9 - 7
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v5):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + zRescale * v9):e}\n',
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v7):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 1\n',  # triangle 8 normal up
                    '       outer loop\n',  # 7 - 9 - 1
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v7):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + zRescale * v9):e}\n',
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v1):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                ]
            )
            # top part ends

            # left side begins
            if x == 0:
                resultfile.writelines(
                    [
                        '   facet normal -1 0 0\n',  # triangle 8- normal left
                        '       outer loop\n',  # 1 - down1 - 7
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v1):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v7):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                        '   facet normal -1 0 0\n',  # triangle 8- normal left
                        '       outer loop\n',  # down1 - down7 - 7
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v7):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                    ]
                )
            # left side ends

            # right side begins
            if x == (X - 1):
                resultfile.writelines(
                    [
                        '   facet normal 1 0 0\n',  # triangle 4+ normal left
                        '       outer loop\n',  # 5 - down5 - 3
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v5):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v3):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                        '   facet normal 1 0 0\n',  # triangle 4+ normal left
                        '       outer loop\n',  # 3 - down5 - down3
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v3):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                    ]
                )
            # right side ends

            # far side begins
            if y == 0:
                resultfile.writelines(
                    [
                        '   facet normal 0 -1 0\n',  # triangle 2- normal far
                        '       outer loop\n',  # 3 - down - 1
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v3):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v1):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                        '   facet normal 0 -1 0\n',  # triangle 2- normal far
                        '       outer loop\n',  # down - down - 1
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + zRescale * v1):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                    ]
                )
            # far side ends

            # close side begins
            if y == (Y - 1):
                resultfile.writelines(
                    [
                        '   facet normal 0 1 0\n',  # triangle 6+ normal close
                        '       outer loop\n',  # 7 - down - 5
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v7):e}\n',
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v5):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                        '   facet normal 0 1 0\n',  # triangle 6+ normal close
                        '       outer loop\n',  # down - down - 5
                        f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                        f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + zRescale * v5):e}\n',
                        '       endloop\n',
                        '   endfacet\n',
                    ]
                )
            # close side ends

            # bottom part begins
            resultfile.writelines(
                [
                    '   facet normal 0 0 -1\n',  # triangle 2 normal up
                    '       outer loop\n',  # 1 - 9 - 3
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 -1\n',  # triangle 4 normal up
                    '       outer loop\n',  # 3 - 9 - 5
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 -1\n',  # triangle 6 normal up
                    '       outer loop\n',  # 5 - 9 - 7
                    f'           vertex {(xRescale * (xWrite + 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                    '   facet normal 0 0 -1\n',  # triangle 8 normal up
                    '       outer loop\n',  # 7 - 9 - 1
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite + 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite + xOffset)):e} {(yRescale * (yWrite + yOffset)):e} {(zOffset + 0.0):e}\n',
                    f'           vertex {(xRescale * (xWrite - 0.5 + xOffset)):e} {(yRescale * (yWrite - 0.5 + yOffset)):e} {(zOffset + 0.0):e}\n',
                    '       endloop\n',
                    '   endfacet\n',
                ]
            )
            # bottom part ends

    resultfile.write('endsolid pryanik_nepechatnyj')  # closing object

    # Close output
    resultfile.close()

    return None


# Procedure end, main body begins
if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
