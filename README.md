
| 【EN】 | [〖RU〗](README.RU.md) |
| ---- | ---- |

# Bitmap to POVRay 3D triangle mesh converter

Python program for conversion of bitmap heightfield (in PNG or PGM/PPM format) to 3D triangle mesh in [POVRay](https://www.povray.org/) POV, Wavefront OBJ, Autodesk DXF and stereolithography (3D printer) STL format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.  

[![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png "Example of img2mesh output rendering")](https://dnyarri.github.io/img2mesh.html)

## Format compatibility

| Import image format | Export 3D mesh format |
| ------ | ------ |
| 16 and 8 bits per channel PNG, PGM and PPM  | POV, OBJ, ASCII STL, ASCII DXF |

## Project content

- [**img2mesh.py**](https://github.com/Dnyarri/img2mesh/blob/main/img2mesh.py) - suitable GUI frontend comprising all programs and functions.

- **list2mesh** module, including:

  - [**list2pov.py**](https://github.com/Dnyarri/img2mesh/blob/main/export/list2pov.py): nested 3D list to POV-Ray scene conversion and output. Exported file contain fully operational scene;

  - [**list2stl.py**](https://github.com/Dnyarri/img2mesh/blob/main/export/list2stl.py): nested 3D list to stereolithography ascii STL object conversion and output. Exported file contain elevation map mesh plus sides and bottom as needed for 3D printer;

  - [**list2obj.py**](https://github.com/Dnyarri/img2mesh/blob/main/export/list2obj.py): nested 3D list to Wavefront OBJ conversion and output. Exported file contain elevation map mesh only;

  - [**list2dxf.py**](https://github.com/Dnyarri/img2mesh/blob/main/export/list2dxf.py): nested 3D list to Autodesk ASCII DXF conversion and output Exported file contain elevation map mesh only;

- **pypng** and **pypnm** modules contain components providing PNG and PPM image files reading as nested 3D lists.

[![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png "Preview of img2mesh output files in one folder")](https://dnyarri.github.io/img2mesh.html)

## Prerequisite and Dependencies

1. [Python](https://www.python.org/) 3.10 or above.
2. [PyPNG](https://gitlab.com/drj11/pypng). Copy included into current img2mesh distribution.
3. [PyPNM](https://pypi.org/project/PyPNM/). Copy included into current img2mesh distribution.
4. Tkinter. Normally included into standard CPython distribution.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box. Program is equipped with minimal GUI, so all you have to do after starting a program is open image file using double-click into dialog or Ctrl+O keys, or bring to life main "FIle" menu with right-click or Alt+F, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with suitable 3D software and render the scene.

### For developers

Export module, containing 3D-export functions, may be copied and used by other developers at will.

## References

1. [POV-Ray](https://www.povray.org/) and POV SDL specifications.

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf) specs from [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Cătălin IANCU et al., From CAD model to 3D print via “STL” file format](https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf).

4. [Marshall Burns, Automated Fabrication, Section 6.5](https://www.fabbers.com/tech/STL_Format).

5. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf) by Autodesk, Inc.

### Related

[Dnyarri website - more Python freeware](https://dnyarri.github.io) by the same author.

[img2mesh page with illustrations](https://dnyarri.github.io/img2mesh.html), explanations etc.

[img2mesh source at github](https://github.com/Dnyarri/img2mesh)

[img2mesh source at gitflic mirror](https://gitflic.ru/project/dnyarri/img2mesh)
