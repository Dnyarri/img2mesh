**(EN)** [(RU)](README.RU.md)

# Bitmap to POVRay 3D triangle mesh converter

Python program for conversion of bitmap heightfield (in [PNG format](http://www.libpng.org/pub/png/)) to 3D triangle mesh in [POVRay](https://www.povray.org/) POV, Wavefront OBJ and stereolithography (3D printer) STL format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.  

![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png)

Project content:

- **img2mesh** - suitable GUI frontend linked to all programs below.

- **img2pov** - PNG to POVRay scene converter. Exported scene contains 3D mesh, bounding box (CSG intersection) to make it solid object with interior, camera and light. Textures are declared separately and easy to edit.

- **img2obj** - PNG to Wavefront OBJ converter. Exported file contains 3D mesh only.

- **img2stl** - PNG to STL converter. Exported file contain 3D mesh with side and bottom meshes necessary for 3D printer software.

Note that img2pov, img2obj and img2stl may be both run as standalone programs and be imported into some other software (currently in main img2mesh).

![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png)

Current dir contain most recent version of img2mesh program. Some previous versions are saved in *"old_versions"* for future alien archeologist to dig.

*Dependencies:* [PyPNG](https://gitlab.com/drj11/pypng), Tkinter. The former is placed in this repo and, thank the Maker, will work right after downloading; the latter included in all typical Python installation.  

*Usage:* programs are equipped with minimal GUI, so all you have to do after starting the program is use standard "Open..." dialog to open image file, then use standard "Save..." to name exported file to be created, then wait while program does the job, then open resulting file with suitable software and render the scene.

More software at:

[Dnyarri website](https://dnyarri.github.io/)

Project mirrors:

[github Dnyarri](https://github.com/Dnyarri/img2mesh)

[gitflic Dnyarri](https://gitflic.ru/project/dnyarri/img2mesh)
