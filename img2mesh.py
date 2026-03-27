#!/usr/bin/env python3

"""
IMG2MESH - Program for conversion of image heightfield to triangle 3D-mesh in different formats
-----------------------------------------------------------------------------------------------

Created by:
`Ilya Razmanov <mailto:ilyarazmanov@gmail.com>`_ aka
`Ilyich the Toad <mailto:amphisoft@gmail.com>`_.

Versions
--------

This is memorial version of img2mesh based on initial mesh geometry №1.

----
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

img2mesh Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh/tree/classic

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh?branch=classic

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.27.27.7'  # 27 Mar 2026
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from time import ctime
from tkinter import Button, Frame, Label, Menu, PhotoImage, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

from pypng import png2list
from pypnm import list2bin, pnm2list

from list2mesh import list2dxf, list2obj, list2pov, list2stl


def DisMiss(event=None) -> None:
    """Kill dialog and continue."""

    sortir.destroy()


def ShowMenu(event) -> None:
    """Pop menu up (or sort of drop it down)."""

    menu01.post(event.x_root, event.y_root)


def ShowInfo(event=None) -> None:
    """Show image information."""

    file_size = Path(sourcefilename).stat().st_size
    file_size_str = f'{file_size / 1048576:.2f} Mb' if (file_size > 1048576) else f'{file_size / 1024:.2f} Kb' if (file_size > 1024) else f'{file_size} bytes'
    showinfo(
        title='Image information',
        message=f'File properties:\nLocation: {sourcefilename}\nSize: {file_size_str}\nLast modified: {ctime(Path(sourcefilename).stat().st_mtime)}',
        detail=f'Image properties, as represented internally:\nWidth: {X} px\nHeight: {Y} px\nChannels: {Z} channel{"s" if Z > 1 else ""}\nColor depth: {maxcolors + 1} gradations/channel',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled."""

    zanyato.config(state='normal')
    zanyato.config(cursor='')
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    sortir.config(cursor='')
    sortir.update()


def UIBusy() -> None:
    """Busy UI state, buttons disabled."""

    zanyato.config(state='disabled')
    zanyato.config(cursor='wait')
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.config(cursor='wait')
    sortir.update()


def GetSource(event=None) -> None:
    """Open source image and redefine other controls state."""

    global zoom_factor, zoom_do, zoom_show, preview, preview_data, info_normal
    global X, Y, Z, maxcolors, image3D, sourcefilename

    zoom_factor = 0

    old_sourcefilename = sourcefilename  # Temporary saving info in case of "Open.." cancel
    sourcefilename = askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm .pnm'), ('Portable network graphics', '.png'), ('Portable any map', '.ppm .pgm .pbm .pnm')])
    if sourcefilename == '':
        sourcefilename = old_sourcefilename
        return

    info_normal = {'txt': f'{Path(sourcefilename).name}', 'fg': 'grey', 'bg': 'grey90'}

    UIBusy()

    if Path(sourcefilename).suffix.lower() == '.png':
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix.lower() in ('.ppm', '.pgm', '.pbm', '.pnm'):
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)

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
    if X + 16 > sortir.winfo_screenwidth() or Y + 152 > sortir.winfo_screenheight():
        zoomOut()  # We'be better be on a safe side of the zoom
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none', background=zanyato.master['background'], relief='flat', borderwidth=1)
    # ↓ binding zoom on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    sortir.bind_all('<Control-i>', ShowInfo)
    # ↓ enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # ↓ updating zoom label display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ enabling "Save as..."
    menu01.entryconfig('Export POV-Ray...', state='normal')  # Instead of name numbers from 0 may be used
    menu01.entryconfig('Export OBJ...', state='normal')
    menu01.entryconfig('Export DXF...', state='normal')
    menu01.entryconfig('Export STL...', state='normal')
    menu01.entryconfig('Image Info...', state='normal')
    UINormal()
    # ↓ updating UI size for opened image
    h_spacer = min(sortir.winfo_reqwidth(), 9 * sortir.winfo_screenwidth() // 10)
    v_spacer = min(sortir.winfo_reqheight(), 9 * sortir.winfo_screenheight() // 10)
    sortir.minsize(h_spacer, v_spacer)
    sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+{(sortir.winfo_screenheight() - sortir.winfo_height()) // 2 - 32}')
    zanyato.focus_set()


def SaveAsPOV() -> None:
    """Once selected Export POV-Ray."""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov .inc'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Mesh_№1.pov',
    )
    if savefilename == '':
        return None

    UIBusy()
    list2pov(image3D, maxcolors, savefilename)
    UINormal()


def SaveAsOBJ() -> None:
    """Once selected Export OBJ."""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save Wavefront OBJ file',
        filetypes=[
            ('Wavefront OBJ', '.obj'),
            ('All Files', '*.*'),
        ],
        defaultextension='.obj',
        initialfile=Path(sourcefilename).stem + '_Mesh_№1.obj',
    )
    if savefilename == '':
        return None

    UIBusy()
    list2obj(image3D, maxcolors, savefilename)
    UINormal()


def SaveAsSTL() -> None:
    """Once selected Export STL."""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save STL file',
        filetypes=[
            ('Stereolithography STL', '.stl'),
            ('All Files', '*.*'),
        ],
        defaultextension='.stl',
        initialfile=Path(sourcefilename).stem + '_Mesh_№1.stl',
    )
    if savefilename == '':
        return None

    UIBusy()
    list2stl(image3D, maxcolors, savefilename)
    UINormal()


def SaveAsDXF() -> None:
    """Once selected Export DXF."""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save Autodesk DXF file',
        filetypes=[
            ('Autodesk DXF', '.dxf'),
            ('All Files', '*.*'),
        ],
        defaultextension='.dxf',
        initialfile=Path(sourcefilename).stem + '_Mesh_№1.dxf',
    )
    if savefilename == '':
        return None

    UIBusy()
    list2dxf(image3D, maxcolors, savefilename)
    UINormal()


def zoomIn(event=None) -> None:
    """Zoom preview in."""

    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5
    preview = PhotoImage(data=preview_data)
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    # ↓ updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 4:  # max zoom 5
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut(event=None) -> None:
    """Zoom preview out."""

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


def zoomWheel(event) -> None:
    """zoomIn or zoomOut by mouse wheel."""

    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

zoom_factor = 0
sourcefilename = X = Y = Z = maxcolors = None
product_name = 'img2mesh'
product_about = f'{product_name} {__version__}'

sortir = Tk()

sortir.title(product_about)

# ↓ ICO icon.
#   Tkinter seem to read icon with index=0 and interpolate to unknown size.
icon_path = Path(__file__).resolve().parent / 'vaba.ico'

if icon_path.exists():
    sortir.iconbitmap(icon_path)
else:
    sortir.iconphoto(True, PhotoImage(data=b'P6\n2 2\n255\n\xff\x00\x00\xff\xff\x00\x00\x00\xff\x00\xff\x00'))

# ↓ Info statuses dictionaries
info_normal = {'txt': product_about, 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}
# ↓ Info string with info statuses above
info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')
# ↓ Info string binding for mouse over
info_string.bind('<Enter>', lambda event=None: info_string.config(text=product_about))
info_string.bind('<Leave>', lambda event=None: info_string.config(text=info_normal['txt']))

menu01 = Menu(sortir, tearoff=False)  # Drop-down
menu01.add_command(label='Open...', state='normal', accelerator='Ctrl+O', command=GetSource)
menu01.add_separator()
menu01.add_command(label='Export POV-Ray...', state='disabled', command=SaveAsPOV)
menu01.add_command(label='Export OBJ...', state='disabled', command=SaveAsOBJ)
menu01.add_command(label='Export DXF...', state='disabled', command=SaveAsDXF)
menu01.add_command(label='Export STL...', state='disabled', command=SaveAsSTL)
menu01.add_separator()
menu01.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu01.add_separator()
menu01.add_command(label='Exit', state='normal', accelerator='Ctrl+Q', command=DisMiss)

sortir.bind('<Button-3>', ShowMenu)
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Alt-F>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-O>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)
sortir.bind_all('<Control-Q>', DisMiss)
sortir.bind_all('<Control-w>', DisMiss)
sortir.bind_all('<Control-W>', DisMiss)

frame_img = Frame(sortir, borderwidth=2, relief='groove')
frame_img.pack(side='top', anchor='center', expand=True)

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
frame_img.bind('<Double-Button-1>', GetSource)
zanyato.pack(side='top', padx=0, pady=(0, 2))

frame_zoom = Frame(frame_img, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

# ↓ Center window horizontally, +100 vertically
sortir.update()
h_spacer = max(frame_img.winfo_reqwidth(), info_string.winfo_reqwidth())
v_spacer = sortir.winfo_reqheight()
sortir.minsize(h_spacer, v_spacer)
sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+100')

sortir.mainloop()
