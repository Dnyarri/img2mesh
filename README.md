# Bitmap to 3D triangle mesh converter

Python utilities for conversion of bitmap heightfield (PNG etc) to 3D triangle mesh in [POVRay](https://www.povray.org/) format. Resulting triangle mesh provides better rendering in case of low-res source files as compared to using source bitmaps as a heightfield directly.

- **ver.01.xxx** - converts 4 x 4 pixel square into 2 triangle. ver.01.003 - folding according to local gradient. Development cancelled at ver.01.004 in favour of ver.02.

- **ver.02.xxx** - converts 1 pixel into pyramid of 4 triangles, significantly improving visual appearance of rendering. Mesh is tight enough to be used in CSG (since version 02.002 added intersection with bounding box, thus giving sides and bottom to mesh).

*Dependencies:* Pillow, Tkinter

*Usage:* programs are equipped with minimal GUI, so all you have to do after starting the programs is use standard "Open..." GUI to open image file, then use standard "Save..." GUI to set POVRay scene file to be created, then wait while program does the job, then open resulting POV file with POVRay and render the scene. Scene contains enough basic stuff (globals, light, camera) to be rendered successfully right after exporting without any editing.

*Example:* Simple black and white drawing, with blurs to simulate bevels etc., after converting using img2mesh.02.004.py and rendering using POVRay.

![Rendering example.](ycoin.png)
