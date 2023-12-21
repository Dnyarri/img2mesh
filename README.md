# Bitmap to 3D triangle mesh converter

Python utilities for conversion of bitmap heightfield (PNG etc) to 3D triangle mesh in POVRay format. Resulting triangle mesh provides better rendering in case of low-res source files.

*ver.01* - converts 4 x 4 pixel square into 2 triangle. ver.01.003 - folding according to local gradient. Development cancelled at ver.01.004 in favour of ver.02.

*ver.02* - converts 1 pixel into pyramid of 4 triangles, significantly improving visual appearance of rendering.

Dependencies: Pillow, Tkinter
