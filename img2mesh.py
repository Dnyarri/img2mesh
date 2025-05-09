#!/usr/bin/env python3

"""
IMG2MESH - Program for conversion of image heightfield to triangle 3D-mesh in different formats
------------------------------------------------------------------------------------------------

Created by:
`Ilya Razmanov <mailto:ilyarazmanov@gmail.com>`_ aka
`Ilyich the Toad <mailto:amphisoft@gmail.com>`_.

History
--------

2.13.13.2   Previous version of img2mesh GUI replaced with completely new joint
(PyPNG, PyPNM) ➔ (list2pov, list2obj, list2stl, list2dxf) program with the same name.

3.14.16.1   list2mesh components upgraded to version 3 with improved geometry.

3.16.20.20  New minimalistic menu-based GUI.

----
Main site: `The Toad's Slimy Mudhole <https://dnyarri.github.io>`_

Git repositories:
`Main at Github <https://github.com/Dnyarri/img2mesh>`_; `Gitflic mirror <https://gitflic.ru/project/dnyarri/img2mesh>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.17.9.12'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from tkinter import Button, Frame, Label, Menu, PhotoImage, Tk, filedialog

from export import list2dxf, list2obj, list2pov, list2stl
from pypng import pnglpng
from pypnm import pnmlpnm


def DisMiss(event=None):
    """Kill dialog and continue"""
    sortir.destroy()


def ShowMenu(event):
    """Pop menu up (or sort of drop it down)"""
    menu01.post(event.x_root, event.y_root)


def UINormal():
    """Normal UI state, buttons enabled"""
    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget.config(state='normal')
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])


def UIBusy():
    """Busy UI state, buttons disabled"""
    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget.config(state='disabled')
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def GetSource(event=None):
    """Opening source image and redefining other controls state"""

    global zoom_factor, zoom_do, zoom_show, preview, preview_data
    global X, Y, Z, maxcolors, image3D, sourcefilename
    global info_normal

    zoom_factor = 0

    sourcefilename = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('PNG', '.png'), ('PNM', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return

    info_normal = {'txt': f'{Path(sourcefilename).name}', 'fg': 'grey', 'bg': 'grey90'}

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        │  They are used during export!          │
        └────────────────────────────────────────┘ """

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
        └────────────────────────────────────────────────────────────────────────-┘ """
    preview_data = pnmlpnm.list2bin(image3D, maxcolors, show_chessboard=True)

    """ ┌────────────────────────────────────────────────┐
        │ Now showing "preview_data" bytes using Tkinter │
        └────────────────────────────────────────────────┘ """
    preview = PhotoImage(data=preview_data)

    zoom_show = {  # What to show below preview
        -4: 'Zoom 1:5',
        -3: 'Zoom 1:4',
        -2: 'Zoom 1:3',
        -1: 'Zoom 1:2',
        0: 'Zoom 1:1',
        1: 'Zoom 2:1',
        2: 'Zoom 3:1',
        3: 'Zoom 4:1',
        4: 'Zoom 5:1',
    }
    zoom_do = {  # What to do to preview; "zoom" zooms in, "subsample" zooms out
        -4: preview.subsample(5, 5),
        -3: preview.subsample(4, 4),
        -2: preview.subsample(3, 3),
        -1: preview.subsample(2, 2),
        0: preview,  # 1:1
        1: preview.zoom(2, 2),
        2: preview.zoom(3, 3),
        3: preview.zoom(4, 4),
        4: preview.zoom(5, 5),
    }

    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none', justify='center', background=zanyato.master['background'], relief='flat', borderwidth=1)
    # binding zoom on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    # enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # updating zoom label display
    label_zoom.config(text=zoom_show[zoom_factor])
    # enabling "Save as..."
    menu01.entryconfig('Export POV-Ray...', state='normal')  # Instead of name numbers from 0 may be used
    menu01.entryconfig('Export OBJ...', state='normal')
    menu01.entryconfig('Export DXF...', state='normal')
    menu01.entryconfig('Export STL...', state='normal')

    UINormal()


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


def zoomIn(event=None):
    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5
    preview = PhotoImage(data=preview_data)
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    # updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 4:  # max zoom 5
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut(event=None):
    global zoom_factor, preview
    zoom_factor = max(zoom_factor - 1, -4)  # min zoom 1/5
    preview = PhotoImage(data=preview_data)
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    # updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == -4:  # min zoom 1/5
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


def zoomWheel(event):
    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

# Starting values
zoom_factor = 0
sourcefilename = X = Y = Z = maxcolors = None

sortir = Tk()

sortir.title('img2mesh')
sortir.geometry('+200+100')
sortir.minsize(128, 128)

icon_path = Path(__file__).resolve().parent / 'vaba.ico'
if icon_path.exists():
    sortir.iconbitmap(str(icon_path))
else:
    sortir.iconphoto(True, PhotoImage(data=b'P6\n2 2\n255\n\xff\x00\x00\xff\xff\x00\x00\x00\xff\x00\xff\x00'))

# Info statuses dictionaries
info_normal = {'txt': f'img2mesh {__version__}', 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

menu01 = Menu(sortir, tearoff=False)  # Drop-down
menu01.add_command(label='Open...', state='normal', accelerator='Ctrl+O', command=GetSource)
menu01.add_separator()
menu01.add_command(label='Export POV-Ray...', state='disabled', command=SaveAsPOV)
menu01.add_command(label='Export OBJ...', state='disabled', command=SaveAsOBJ)
menu01.add_command(label='Export DXF...', state='disabled', command=SaveAsDXF)
menu01.add_command(label='Export STL...', state='disabled', command=SaveAsSTL)
menu01.add_separator()
menu01.add_command(label='Exit', state='normal', accelerator='Ctrl+Q', command=DisMiss)

sortir.bind('<Button-3>', ShowMenu)
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)

frame_img = Frame(sortir, borderwidth=2, relief='groove')
frame_img.pack(side='top')

zanyato = Label(
    frame_img,
    text='Preview area.\n  Double click to open image,\n  Right click or Alt+F for a menu.\nWith image opened,\n  Ctrl+Click to zoom in,\n  Alt+Click to zoom out.',
    font=('helvetica', 12),
    justify='left',
    borderwidth=2,
    padx=24,
    pady=24,
    relief='groove',
    background='grey90',
    cursor='arrow',
)
zanyato.bind('<Double-Button-1>', GetSource)
zanyato.pack(side='top', padx=0, pady=(0, 2))

frame_zoom = Frame(frame_img, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
