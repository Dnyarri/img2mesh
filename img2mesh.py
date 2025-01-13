#!/usr/bin/env python3

"""
IMG2MESH - Program for conversion of image heightfield to triangle 3D-mesh in different formats
------------------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com) aka Ilyich the Toad (mailto:amphisoft@gmail.com)

History:
---------

2.13.13.2   Previous version of img2mesh GUI replaced with completely new joint (PyPNG, PyPNM) ➔ (list2pov, list2obj, list2stl, list2dxf) program with the same name.

-------------------
Main site:  
https://dnyarri.github.io  

Project mirrored at:  
https://github.com/Dnyarri/img2mesh  
https://gitflic.ru/project/dnyarri/img2mesh  

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '2.13.13.2'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from tkinter import Button, Frame, Label, PhotoImage, Tk, filedialog

from list2mesh import list2dxf, list2obj, list2pov, list2stl
from pypng import pnglpng
from pypnm import pnmlpnm


def DisMiss():
    """Kill dialog and continue"""

    sortir.destroy()


def GetSource():
    """Opening source image and redefining other controls state"""

    global zoom_factor, sourcefilename, preview, preview_data
    zoom_factor = 1
    sourcefilename = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('PNG', '.png'), ('PNM', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        └───────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    """ ┌─────────────────────────────────────────────────────────────────────────┐
        │ Converting list to bytes of PPM-like structure "preview_data" in memory │
        └─────────────────────────────────────────────────────────────────────────┘ """
    preview_data = pnmlpnm.list2bin(image3D, maxcolors)

    """ ┌────────────────────────────────────────────────┐
        │ Now showing "preview_data" bytes using Tkinter │
        └────────────────────────────────────────────────┘ """
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)  # "zoom" zooms in, "subsample" zooms out
    zanyato.config(text='Source', image=preview, compound='top')

    """ ┌──────────────────────────┐
        │ Updating controls status │
        └──────────────────────────┘ """
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # updating "Export..." status
    butt02.config(state='normal', cursor='hand2')
    butt03.config(state='normal', cursor='hand2')
    butt04.config(state='normal', cursor='hand2')
    butt05.config(state='normal', cursor='hand2')


def SaveAsPOV():
    """Once pressed on Export POV"""

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        └───────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    # Open "Save as..." file
    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov .inc'),
            ('All Files', '*.*'),
        ],
        defaultextension=('POV-Ray scene file', '.pov'),
    )
    if savefilename == '':
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    info_string.config(text='BUSY PROCESSING, PLEASE WAIT', foreground='red')
    sortir.update()

    list2pov.list2pov(image3D, maxcolors, savefilename)

    info_string.config(text='Bitmap height field to 3D mesh converter', foreground='grey')


def SaveAsOBJ():
    """Once pressed on Export OBJ"""

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        └───────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    # Open "Save as..." file
    savefilename = filedialog.asksaveasfilename(
        title='Save Wavefront OBJ file',
        filetypes=[
            ('Wavefront OBJ', '.obj'),
            ('All Files', '*.*'),
        ],
        defaultextension=('Wavefront OBJ', '.obj'),
    )
    if savefilename == '':
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to OBJ and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    info_string.config(text='BUSY PROCESSING, PLEASE WAIT', foreground='red')
    sortir.update()

    list2obj.list2obj(image3D, maxcolors, savefilename)

    info_string.config(text='Bitmap height field to 3D mesh converter', foreground='grey')


def SaveAsSTL():
    """Once pressed on Export STL"""

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        └───────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    # Open "Save as..." file
    savefilename = filedialog.asksaveasfilename(
        title='Save STL file',
        filetypes=[
            ('Stereolithography STL', '.stl'),
            ('All Files', '*.*'),
        ],
        defaultextension=('Stereolithography STL', '.stl'),
    )
    if savefilename == '':
        info_string.config(text='Bitmap height field to 3D mesh converter', foreground='grey')
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to STL and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    info_string.config(text='BUSY PROCESSING, PLEASE WAIT', foreground='red')
    sortir.update()

    list2stl.list2stl(image3D, maxcolors, savefilename)

    info_string.config(text='Bitmap height field to 3D mesh converter', foreground='grey')


def SaveAsDXF():
    """Once pressed on Export DXF"""

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        └───────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    # Open "Save as..." file
    savefilename = filedialog.asksaveasfilename(
        title='Save Autodesk DXF file',
        filetypes=[
            ('Autodesk DXF', '.dxf'),
            ('All Files', '*.*'),
        ],
        defaultextension=('Autodesk DXF', '.dxf'),
    )
    if savefilename == '':
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to DXF and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    info_string.config(text='BUSY PROCESSING, PLEASE WAIT', foreground='red')
    sortir.update()

    list2dxf.list2dxf(image3D, maxcolors, savefilename)

    info_string.config(text='Bitmap height field to 3D mesh converter', foreground='grey')


def zoomIn():
    """Zoom +"""
    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 3)  # max zoom 3
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(text='Source', image=preview, compound='top')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 3:  # max zoom 3
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut():
    """Zoom -"""
    global zoom_factor, preview
    zoom_factor = max(zoom_factor - 1, 1)  # min zoom 1
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(text='Source', image=preview, compound='top')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == 1:  # min zoom 1
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

sortir = Tk()

zoom_factor = 1

iconpath = Path(__file__).resolve().parent / 'vaba.ico'
if iconpath.exists():
    sortir.iconbitmap(str(iconpath))
else:
    sortir.iconphoto(True, PhotoImage(data=b'P6\n2 2\n255\n\xff\x00\x00\xff\xff\x00\x00\x00\xff\x00\xff\x00'))

sortir.title(f'img2mesh v. {__version__}')
sortir.geometry('+200+100')
sortir.minsize(300, 100)

info_string = Label(sortir, text='Bitmap height field to 3D mesh converter', font=('courier', 8),  foreground='grey')
info_string.pack(side='bottom', padx=0, pady=1, fill='both')

frame_left = Frame(sortir, borderwidth=2, relief='groove')
frame_left.pack(side='left', anchor='nw')
frame_right = Frame(sortir, borderwidth=2, relief='groove')
frame_right.pack(side='right', anchor='nw')

butt01 = Button(frame_left, text='Open image...', font=('arial', 14), cursor='hand2', justify='center', command=GetSource)
butt01.pack(side='top', padx=4, pady=[4, 12], fill='both')

butt02 = Button(frame_left, text='Export POV...', font=('arial', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsPOV)
butt02.pack(side='top', padx=4, pady=2, fill='both')

butt03 = Button(frame_left, text='Export OBJ...', font=('arial', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsOBJ)
butt03.pack(side='top', padx=4, pady=2, fill='both')

butt04 = Button(frame_left, text='Export STL...', font=('arial', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsSTL)
butt04.pack(side='top', padx=4, pady=2, fill='both')

butt05 = Button(frame_left, text='Export DXF...', font=('arial', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsDXF)
butt05.pack(side='top', padx=4, pady=2, fill='both')

butt99 = Button(frame_left, text='Exit', font=('arial', 14), cursor='hand2', justify='center', command=DisMiss)
butt99.pack(side='bottom', padx=4, pady=[12, 4], fill='both')

zanyato = Label(frame_right, text='Preview area', font=('arial', 10), justify='center', borderwidth=2, relief='groove')
zanyato.pack(side='top')

frame_zoom = Frame(frame_right, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text=f'Zoom {zoom_factor}:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
