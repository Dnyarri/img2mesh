#!/usr/bin/env python3

"""
========
IMG2MESH
========

Program for conversion of image heightfield
to triangle 3D-mesh in various formats.

History
-------

2.13.13.2   Previous version of img2mesh GUI replaced with completely new
joint (PyPNG, PyPNM) ➔ (list2pov, list2obj, list2stl, list2dxf)
program with the same name.

3.14.16.1   list2mesh components upgraded to version 3 with improved geometry.

3.16.20.20  New minimalistic menu-based GUI.

3.21.19.19  GUI changed to add threshold input for new Geometry №3+.

3.23.4.23   Validation was inevitably added to threshold input.

----
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

`img2mesh`_ explanations and illustrations page.

.. _img2mesh: https://dnyarri.github.io/img2mesh.html

img2mesh Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2025-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.27.8.1'  # 8 Mar 2026
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from time import ctime
from tkinter import Button, DoubleVar, Frame, Label, Menu, Menubutton, PhotoImage, Spinbox, Tk
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

    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget['state'] = 'normal'
    for widget in frame_control.winfo_children():
        if widget.winfo_class() in ('Label', 'Spinbox'):
            widget['state'] = 'normal'
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    sortir.update()


def UIBusy() -> None:
    """Busy UI state, buttons disabled."""

    for widget in frame_img.winfo_children():
        if widget.winfo_class() in ('Label', 'Button'):
            widget['state'] = 'disabled'
    for widget in frame_control.winfo_children():
        if widget.winfo_class() in ('Label', 'Spinbox'):
            widget['state'] = 'disabled'
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def GetSource(event=None) -> None:
    """Open source image and redefine other controls state."""

    global zoom_factor, zoom_do, zoom_show, info_normal
    global sourcefilename, X, Y, Z, maxcolors, image3D
    global preview, preview_data

    zoom_factor = 0

    old_sourcefilename = sourcefilename  # Temporary saving info in case of "Open.." cancel
    sourcefilename = askopenfilename(
        title='Open image file',
        filetypes=[('Supported formats', '.png .ppm .pgm .pbm .pnm'), ('Portable network graphics', '.png'), ('Portable any map', '.ppm .pgm .pbm .pnm')],
    )
    if sourcefilename == '':
        sourcefilename = old_sourcefilename
        return

    info_normal = {'txt': f'{Path(sourcefilename).name}', 'fg': 'grey', 'bg': 'grey90'}

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        │  They are used during export!          │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix.lower() == '.png':
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix.lower() in ('.ppm', '.pgm', '.pbm', '.pnm'):
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    """ ┌─────────────────────────────────────────────────────────────────────────┐
        │ Converting list to bytes of PPM-like structure "preview_data" in memory │
        └────────────────────────────────────────────────────────────────────────-┘ """
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)

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
    zanyato.config(image=preview, compound='none', background=zanyato.master['background'], relief='flat', borderwidth=1)
    zanyato.pack_configure(pady=max(0, 16 - (preview.height() // 2)))

    """ ┌────────────────────────────────────────────┐
        │ Binding everything that needs opened image │
        └────────────────────────────────────────────┘ """
    # ↓ binding zoom
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    # ↓ image info
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
    sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+{(sortir.winfo_screenheight() - sortir.winfo_height()) // 2 - 32}')


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
        initialfile=Path(sourcefilename).stem + '_Mesh.pov',
    )
    if savefilename == '':
        return None

    # ↓ Converting list to POV and saving as "savefilename"
    UIBusy()
    list2pov(image3D, maxcolors, savefilename, threshold=float(geometry_threshold.get()))
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
        initialfile=Path(sourcefilename).stem + '.obj',
    )
    if savefilename == '':
        return None

    # ↓ Converting list to OBJ and saving as "savefilename"
    UIBusy()
    list2obj(image3D, maxcolors, savefilename, threshold=float(geometry_threshold.get()))
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
        initialfile=Path(sourcefilename).stem + '.stl',
    )
    if savefilename == '':
        return None

    # ↓ Converting list to STL and saving as "savefilename"
    UIBusy()
    list2stl(image3D, maxcolors, savefilename, threshold=float(geometry_threshold.get()))
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
        initialfile=Path(sourcefilename).stem + '.dxf',
    )
    if savefilename == '':
        return None

    # ↓ Converting list to DXF and saving as "savefilename"
    UIBusy()
    list2dxf(image3D, maxcolors, savefilename, threshold=float(geometry_threshold.get()))
    UINormal()


def zoomIn(event=None) -> None:
    """Zoom preview in."""

    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5
    preview = PhotoImage(data=preview_data)
    preview = zoom_do[zoom_factor]
    zanyato.config(image=preview, compound='none')
    zanyato.pack_configure(pady=max(0, 16 - (preview.height() // 2)))
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
    zanyato.pack_configure(pady=max(0, 16 - (preview.height() // 2)))
    # ↓ updating zoom factor display
    label_zoom.config(text=zoom_show[zoom_factor])
    # ↓ reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == -4:  # min zoom 1/5
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


def zoomWheel(event) -> None:
    """zoomIn or zoomOut by mouse wheel."""

    if event.widget != spin01:  # Blocks spinbox from zoomWheel for incWheel
        if event.delta < 0:
            zoomOut()
        if event.delta > 0:
            zoomIn()


def incWheel(event) -> None:
    """Increment or decrement entry value by mouse wheel."""

    if event.widget == spin01:
        if event.delta < 0:
            geometry_threshold.set(round(min(1.0, max(0.0, geometry_threshold.get() - 0.01)), 2))
        if event.delta > 0:
            geometry_threshold.set(round(min(1.0, max(0.0, geometry_threshold.get() + 0.01)), 2))


def valiDig(new_value):
    """Try to validate float input."""

    try:
        _ = float(new_value)
        if _ >= 0 and _ <= 1.0:
            return True
        else:
            return False
    except ValueError:
        return False


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """
# ↓ Initializing
sourcefilename = ''
zoom_factor = 0
X = Y = Z = maxcolors = None

sortir = Tk()

sortir.title('img2mesh')

# ↓ ICO icon.
#   Tkinter seem to read icon with index=0 and interpolate to unknown size.
icon_path = Path(__file__).resolve().parent / 'vaba.ico'

if icon_path.exists():
    sortir.iconbitmap(icon_path)
else:  # New brighter OYMC alt icon for a new year!
    sortir.iconphoto(True, PhotoImage(data=b'P6\n2 2\n255\n\xff\x7f\x00\xff\xff\x00\xff\x00\xff\x00\xff\xff'))

# ↓ Spinbox manual input validation.
validate_entry = sortir.register(valiDig)

# ↓ Info statuses dictionaries
info_normal = {
    'txt': f'img2mesh {__version__}',
    'fg': 'grey',
    'bg': 'grey90',
}
info_busy = {
    'txt': 'BUSY, PLEASE WAIT',
    'fg': 'red',
    'bg': 'yellow',
}

# ↓ Buttons dictionaries
butt = {
    'font': ('helvetica', 12),
    'cursor': 'hand2',
    'border': '2',
    'relief': 'groove',
    'overrelief': 'ridge',
    'foreground': 'SystemButtonText',
    'background': 'SystemButtonFace',
    'activeforeground': 'dark blue',
    'activebackground': '#E5F1FB',
}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

frame_control = Frame(sortir, borderwidth=2, relief='groove')
frame_control.pack(side='top', anchor='nw', expand=False)

# ↓ File menu
butt_file = Menubutton(
    frame_control,
    text='File...'.ljust(10, ' '),
    font=butt['font'],
    cursor=butt['cursor'],
    relief=butt['relief'],
    activeforeground=butt['activeforeground'],
    activebackground=butt['activebackground'],
    border=butt['border'],
    state='normal',
    indicatoron=False,
)
butt_file.pack(side='left', fill='both')

menu01 = Menu(butt_file, tearoff=False)  # Drop-down
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

butt_file['menu'] = menu01

# ↓ Threshold control
info01 = Label(frame_control, text='Threshold:', font=(butt['font'][0], butt['font'][1] - 2), state='disabled')
info01.pack(side='left', padx=(24, 2))

geometry_threshold = DoubleVar(value=0.05)
spin01 = Spinbox(
    frame_control,
    from_=0,
    to=1.0,
    increment=0.01,
    textvariable=geometry_threshold,
    state='disabled',
    width=5,
    font=butt['font'],
    validate='key',
    validatecommand=(validate_entry, '%P'),
)
spin01.pack(side='right', fill='y')

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
zanyato.pack(side='top', padx=0, pady=0)

frame_zoom = Frame(frame_img, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

""" ┌────────────────────────────────────────────────────┐
    │ Binding everything that does not need opened image │
    └────────────────────────────────────────────────────┘ """
# ↓ Spinbox mouseovers
spin01.bind('<Enter>', lambda event=None: spin01.config(foreground=butt['activeforeground'], background=butt['activebackground']))
spin01.bind('<Leave>', lambda event=None: spin01.config(foreground=butt['foreground'], background='white'))
# ↓ Spinbox mousewheel
spin01.unbind('<MouseWheel>')
spin01.bind('<MouseWheel>', incWheel)
# ↓ Double-click to open image
zanyato.bind('<Double-Button-1>', GetSource)
frame_img.bind('<Double-Button-1>', GetSource)
# ↓ "File..." mouseover
butt_file.bind('<Enter>', lambda event=None: butt_file.config(relief=butt['overrelief']))
butt_file.bind('<Leave>', lambda event=None: butt_file.config(relief=butt['relief']))
# ↓ Global stuff
sortir.bind('<Button-3>', ShowMenu)
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Alt-F>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-O>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)
sortir.bind_all('<Control-Q>', DisMiss)
sortir.bind_all('<Control-w>', DisMiss)
sortir.bind_all('<Control-W>', DisMiss)

# ↓ Center window horizontally, +100 vertically
sortir.update()
sortir.minsize(frame_control.winfo_width(), 128)
sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+100')

sortir.mainloop()
