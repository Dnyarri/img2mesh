#!/usr/bin/env python3

"""
IMG2POV - Program for conversion of image heightfield to triangle mesh in POV-Ray format
----------------------------------------------------------------------------------------

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com) aka Ilyich the Toad (mailto:amphisoft@gmail.com)

History:

2.13.4.0    Shell for list2pov.

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
__version__ = '2.14.1.1'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from pathlib import Path
from tkinter import BOTH, Label, Tk, filedialog

from list2mesh import list2pov
from pypng import pnglpng
from pypnm import pnmlpnm

""" ╔═════════════════╗
    ║ Creating dialog ║
    ╚═════════════════╝ """

sortir = Tk()
sortir.title('Image to POV-Ray conversion')
iconpath = Path(__file__).resolve().parent / 'vaba.ico'
if iconpath.exists():
    sortir.iconbitmap(str(iconpath))
sortir.geometry(f'200x64+{(sortir.winfo_screenwidth()-200)//2}+{(sortir.winfo_screenheight()-64)//2}')
sortir.resizable(width=True, height=True)
zanyato = Label(sortir, text='Starting...', font=('helvetica', 16), padx=24, pady=10, justify='center')
zanyato.pack(fill=BOTH, expand=True)
sortir.overrideredirect(True)
sortir.withdraw()
# Main dialog created and hidden

""" ╔═══════════════╗
    ║ Opening files ║
    ╚═══════════════╝ """

# Open source image, first get name
source_file_name = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('PNG', '.png'), ('PNM', '.ppm .pgm .pbm')])
if (source_file_name == '') or (source_file_name is None):
    sortir.destroy()
    quit()

if Path(source_file_name).suffix == '.png':
    # Reading image as list
    X, Y, Z, maxcolors, image3d, info = pnglpng.png2list(source_file_name)

elif Path(source_file_name).suffix in ('.ppm', '.pgm', '.pbm'):
    # Reading image as list
    X, Y, Z, maxcolors, image3d = pnmlpnm.pnm2list(source_file_name)

else:
    raise ValueError('Extension not recognized')

# get the name of result file to be opened later
result_file_name = filedialog.asksaveasfilename(
    title='Save POV-Ray file',
    filetypes=[
        ('POV-Ray file', '.pov .inc'),
        ('All Files', '*.*'),
    ],
    defaultextension=('POV-Ray scene file', '.pov'),
)
if (result_file_name == '') or (result_file_name is None):
    sortir.destroy()
    quit()

# Updating dialog
sortir.deiconify()
zanyato.config(text='Processing...')
sortir.update()
sortir.update_idletasks()

""" ╔══════════════════════╗
    ║ Main part - list2pov ║
    ╚══════════════════════╝ """

list2pov.list2pov(image3d, maxcolors, result_file_name)

sortir.destroy()
sortir.mainloop()
