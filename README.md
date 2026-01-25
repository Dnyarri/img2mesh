
| 【EN】 | [〖RU〗](README.RU.md "img2mesh разъяснена по-русски") |
| ---- | ---- |

# Bitmap to POV-Ray 3D triangle mesh converter

Python program for conversion of bitmap heightfield (in PNG or PGM/PPM format) to 3D triangle mesh in [POV-Ray](https://www.povray.org/ "Persistence of Vision Raytracer") POV, Wavefront OBJ, Autodesk DXF and stereolithography (3D printer) STL format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.  

| Fig. 1. *Example of img2mesh output rendering* |
| :---: |
| [![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png "Example of img2mesh output rendering")](https://dnyarri.github.io/img2mesh.html) |
| *Example of rendering obtained from black and white drawing (made in Inkscape from text and circle, with a bit of Gaussian Blur added in GIMP) after conversion to 3D mesh with img2mesh and changing texture from default to metallic in POV-Ray.* |

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

| Fig. 2. *Preview of img2mesh output files* |
| :---: |
| [![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png "Preview of img2mesh output files in one folder")](https://dnyarri.github.io/img2mesh.html) |
| *Simple example of img2mesh output in different formats: a screenshot of Windows Explorer showing thumbnails for misc. files created by img2mesh from one input "in.png" map.* |

## Prerequisite and Dependencies

1. [Python](https://www.python.org/ "CPython") 3.11 or above.
2. [PyPNG](https://gitlab.com/drj11/pypng "Pure Python PNG format module"). Copy included into current img2mesh distribution.
3. [PyPNM](https://pypi.org/project/PyPNM/ "Pure Python PPM and PGM format module"). Copy included into current img2mesh distribution.
4. Tkinter. Normally included into standard CPython distribution.

> [!NOTE]
> Since img2mesh 3.21.2.16 PyPNM version included into distribution updated to [PyPNM "Victory 2" main](https://github.com/Dnyarri/PyPNM "Pure Python PPM and PGM format module"), intended to be used with Python 3.11 and above. The only actual limitation is that main version does not have a workaround for displaying 16 bpc images necessary for old Tkinter included into old CPython distributions. If you want bringing old Tkinter compatibility back, download [PyPNM extended compatibility version](https://github.com/Dnyarri/PyPNM/tree/py34 "Pure Python PPM and PGM format module for Python 3.4") and plug it in to downgrade img2mesh manually.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box assuming standard CPython is installed on your system. Program is equipped with minimal GUI, so all you have to do after starting a program is open image file using double-click into dialog or Ctrl+O keys, or bring to life main "File" menu with right-click or Alt+F, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with suitable 3D software and render the scene.

> [!NOTE]
> Since img2mesh 3.21.21.21 mesh geometry changed from *ver. 3* to *3+*, which is a hybrid of two approaches - *ver. 3* gives better results for most areas, while newly added *+* works better on sharp diagonal transitions.

Geometry variants switch depending on local contrast, and threshold control is added to GUI. Default threshold setting is based on some experiments but still may need several retries on some objects. But we keep our experiments going; our main goal surely is public heath (c) Dr. Zhbach.

### For developers

Export module, containing 3D-export functions, may be copied and used by other developers at will.

## References

1. [POV-Ray](https://www.povray.org/ "Persistence of Vision Raytracer") and [POV SDL specifications](https://www.povray.org/documentation/3.7.0/ "POV format specifications").

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf "OBJ format specifications") specs from [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Cătălin IANCU et al., From CAD model to 3D print via “STL” file format](https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf "STL format specifications").

4. [Marshall Burns, Automated Fabrication, Section 6.5](https://www.fabbers.com/tech/STL_Format "STL format specifications").

5. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf "DXF format specifications") by Autodesk, Inc.

### Related

[Dnyarri website - more Python freeware for image processing, 3D, and batch automation](https://dnyarri.github.io "The Toad's Slimy Mudhole - Python freeware for POV-Ray and other 3D, Scale2x, Scale3x, Scale2xSFX, Scale3xSFX, PPM and PGM image support, bilinear and barycentric image interpolation, and batch processing") by the same author.

[img2mesh page with illustrations](https://dnyarri.github.io/img2mesh.html "img2mesh page with illustrated explanations and explained illustrations"), explanations etc.

[img2mesh source and binaries at Github](https://github.com/Dnyarri/img2mesh "img2mesh source at Github")

[img2mesh source at Gitflic mirror](https://gitflic.ru/project/dnyarri/img2mesh "img2mesh source at Gitflic mirror")
