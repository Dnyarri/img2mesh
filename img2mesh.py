#!/usr/bin/env python3

"""
IMG2MESH - Program for conversion of image heightfield to triangle 3D-mesh in different formats
------------------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com) aka Ilyich the Toad (mailto:amphisoft@gmail.com)

History:
---------

2.13.13.2   Previous version of img2mesh GUI replaced with completely new joint (PyPNG, PyPNM) ➔ (list2pov, list2obj, list2stl, list2dxf) program with the same name.

3.14.16.1   list2pov upgraded to version 3 with improved geometry.

-------------------
Main site:
https://dnyarri.github.io

Git repository:
https://github.com/Dnyarri/img2mesh; mirror: https://gitflic.ru/project/dnyarri/img2mesh

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.14.19.10'
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


def UINormal():
    """Normal UI state, buttons enabled"""
    for widget in frame_left.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget.config(state='normal')
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])


def UIBusy():
    """Busy UI state, buttons disabled"""
    for widget in frame_left.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget.config(state='disabled')
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def GetSource():
    """Opening source image and redefining other controls state"""

    global zoom_factor, sourcefilename, preview, preview_data
    global maxcolors, image3D
    zoom_factor = 1
    sourcefilename = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('PNG', '.png'), ('PNM', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return None

    """ ┌───────────────────────────────────────┐
        │ Loading file, converting data to list │
        │ NOTE: maxcolors, image3D are GLOBALS! │
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
        return None

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    UIBusy()

    list2pov.list2pov(image3D, maxcolors, savefilename)

    UINormal()


def SaveAsOBJ():
    """Once pressed on Export OBJ"""
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
        return None

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to OBJ and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    UIBusy()

    list2obj.list2obj(image3D, maxcolors, savefilename)

    UINormal()


def SaveAsSTL():
    """Once pressed on Export STL"""
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
        UINormal()
        return None

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to STL and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    UIBusy()

    list2stl.list2stl(image3D, maxcolors, savefilename)

    UINormal()


def SaveAsDXF():
    """Once pressed on Export DXF"""
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
        return None

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to DXF and saving as "savefilename" │
        └─────────────────────────────────────────────────────┘ """

    UIBusy()

    list2dxf.list2dxf(image3D, maxcolors, savefilename)

    UINormal()


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
sortir.minsize(300, 320)

# Info statuses dictionaries
info_normal = {'txt': 'Bitmap height field to 3D mesh converter', 'fg': 'grey', 'bg': 'light grey'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 8), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=1, fill='both')

frame_left = Frame(sortir, borderwidth=2, relief='groove')
frame_left.pack(side='left', anchor='nw')
frame_right = Frame(sortir, borderwidth=2, relief='groove')
frame_right.pack(side='right', anchor='nw')

butt01 = Button(frame_left, text='Open image...'.center(30, ' '), font=('helvetica', 14), cursor='hand2', justify='center', command=GetSource)
butt01.pack(side='top', padx=4, pady=[4, 12], fill='both')

butt02 = Button(frame_left, text='Export POV...', font=('helvetica', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsPOV)
butt02.pack(side='top', padx=4, pady=2, fill='both')

butt03 = Button(frame_left, text='Export OBJ...', font=('helvetica', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsOBJ)
butt03.pack(side='top', padx=4, pady=2, fill='both')

butt04 = Button(frame_left, text='Export STL...', font=('helvetica', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsSTL)
butt04.pack(side='top', padx=4, pady=2, fill='both')

butt05 = Button(frame_left, text='Export DXF...', font=('helvetica', 14), cursor='arrow', justify='center', state='disabled', command=SaveAsDXF)
butt05.pack(side='top', padx=4, pady=2, fill='both')

butt99 = Button(frame_left, text='Exit', font=('helvetica', 14), cursor='hand2', justify='center', command=DisMiss)
butt99.pack(side='bottom', padx=4, pady=[24, 4], fill='both')

zanyato = Label(frame_right, text='Preview area', font=('helvetica', 10), justify='center', borderwidth=2, relief='groove')
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
