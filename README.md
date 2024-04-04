**(EN)** [(RU)](README.RU.md)

# Bitmap to POVRay 3D triangle mesh converter

Python program for conversion of bitmap heightfield (in [PNG format](http://www.libpng.org/pub/png/)) to 3D triangle mesh in [POVRay](https://www.povray.org/) format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.

![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png)

Current dir contain most recent version of img2mesh program. Some previous versions are saved in *"old_versions"* for future alien archeologist to dig.

*Dependencies:* [PyPNG](https://gitlab.com/drj11/pypng), Tkinter. The former is placed in this repo and, thank the Maker, will work right after downloading; the latter included in all typical Python installation.  

*Usage:* program equipped with minimal GUI, so all you have to do after starting the program is use standard "Open..." GUI to open image file, then use standard "Save..." GUI to set POVRay scene file to be created, then wait while program does the job, then open resulting POV file with POVRay and render the scene. Scene contains enough basic stuff (globals, light, camera) to be rendered successfully right after exporting without any editing.

More software at:

[Dnyarri website](https://dnyarri.github.io/)

Project mirrors:

[github Dnyarri](https://github.com/Dnyarri/img2mesh)

[gitflic Dnyarri](https://gitflic.ru/project/dnyarri/img2mesh)
