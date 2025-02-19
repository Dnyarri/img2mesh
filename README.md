
| 【EN】 | [〖RU〗](README.RU.md) |
| ---- | ---- |

# Bitmap to POVRay 3D triangle mesh converter

Python program for conversion of bitmap heightfield (in [PNG](http://www.libpng.org/pub/png/) or [PGM/PPM](https://dnyarri.github.io/pypnm.html) format) to 3D triangle mesh in [POVRay](https://www.povray.org/) POV, Wavefront OBJ, Autodesk DXF and stereolithography (3D printer) STL format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.  

[![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png)](https://dnyarri.github.io/img2mesh.html)

## Format compatibility

| Import image format | Export 3D mesh format |
| ------ | ------ |
| 16 and 8 bits per channel PNG, PGM and PPM  | POV, OBJ, ASCII STL, ASCII DXF |

## Project content

- **img2mesh** - suitable GUI frontend comprising all programs and functions.

- **list2mesh** module, including:

  - **list2pov**: nested 3D list to POV-Ray scene conversion and output. Exported file contain fully operational scene;

  - **list2stl**: nested 3D list to stereolithography ascii STL object conversion and output. Exported file contain elevation map mesh plus sides and bottom as needed for 3D printer;

  - **list2obj**: nested 3D list to Wavefront OBJ conversion and output. Exported file contain elevation map mesh only;

  - **list2dxf**: nested 3D list to Autodesk ascii DXF conversion and output Exported file contain elevation map mesh only;

- **pypng** and **pypnm** modules contain components providing PNG and PPM image files reading as nested 3D lists.

[![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png)](https://dnyarri.github.io/img2mesh.html)

## Dependencies

1. [PyPNG](https://gitlab.com/drj11/pypng). Copy included into current img2mesh distribution.
2. [PyPNM](https://pypi.org/project/PyPNM/). Copy included into current img2mesh distribution.
3. Tkinter. Included into standard CPython distribution.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box. Program is equipped with minimal GUI, so all you have to do after starting a program is use "Open..." dialog to open image file, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with suitable 3D software and render the scene.

### For developers

Module list2mesh, including 3D-export functions, may be copied and used by other developers at will.

## References

1. [POV-Ray](https://www.povray.org/) and POV SDL specifications.

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf) specs from [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Stereo Lithography Files (.stl)](https://paulbourke.net/dataformats/stl/) brief description [*ibid*](https://paulbourke.net/dataformats/).

4. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf) by Autodesk, Inc.

### Related

[Dnyarri website](https://dnyarri.github.io) - the rest of Dnyarri stuff with previews etc.

[github Dnyarri](https://github.com/Dnyarri/img2mesh)

[gitflic Dnyarri](https://gitflic.ru/project/dnyarri/img2mesh)
