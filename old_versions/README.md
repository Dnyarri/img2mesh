**(EN)** [(RU)](README.RU.md)

# Bitmap to 3D triangle mesh converter

Python utilities for conversion of bitmap heightfield (in [PNG format](http://www.libpng.org/pub/png/)) to 3D triangle mesh in [POVRay](https://www.povray.org/) format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.

![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png)

*Version history*

- **img2mesh.01.xxx** - converts 2x2 pixel square into 2 triangle. ver.01.003 - folding according to local gradient. **Development cancelled at ver.01.004 in favour of ver.02**, which provides better rendering.

- **img2mesh.02.xxx** - converts 1 pixel into pyramid of 4 triangles, significantly improving visual appearance of rendering. Mesh is tight enough to be used in [CSG](https://www.povray.org/documentation/3.7.0/r3_4.html#r3_4_5_4) (since version 02.002 added intersection with bounding box, thus giving sides and bottom to mesh).

- **img2mesh.02.005** - major internal change. Input module changed from Pillow to [PyPNG](https://gitlab.com/drj11/pypng) thus allowing 16 bpc PNG files to be processed, generating meshes with higher z-resolution.

- **img2mesh.02.007** - moderate internal changes; **Windows img2mesh.exe** file generated and added to 2.6.1 release.

*Dependencies:* Tkinter, PyPNG / Pillow

*Usage:* programs are equipped with minimal GUI, so all you have to do after starting the programs is use standard "Open..." GUI to open image file, then use standard "Save..." GUI to set POVRay scene file to be created, then wait while program does the job, then open resulting POV file with POVRay and render the scene. Scene contains enough basic stuff (globals, light, camera) to be rendered successfully right after exporting without any editing.

More software at:

[Dnyarri website](https://dnyarri.github.io/)

Project mirrors:

[github Dnyarri](https://github.com/Dnyarri/img2mesh)

[gitflic Dnyarri](https://gitflic.ru/project/dnyarri/img2mesh)
