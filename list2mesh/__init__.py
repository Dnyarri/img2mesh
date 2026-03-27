"""3D nested list to 3D triangle mesh export, Geometry №1.

=========
list2mesh
=========
----------------------------------------------------------------------
Conversion of image heightfield to 3D triangle mesh in various formats
----------------------------------------------------------------------

Overview
--------

**list2mesh** export module present function for converting images
and image-like nested lists to 3D triangle mesh height field,
and saving mesh thus obtained in different ASCII 3D scene/object formats.

Formats comprised by **list2mesh** are:

- POV-Ray Mesh [1]_;
- Wavefront OBJ [2]_;
- Autodesk DXF [3]_;
- Stereolithography STL [4]_.

Usage example
-------------

::

    from list2mesh import list2pov
    list2pov(image3d, maxcolors, result_file_name)

where:

- **``image3d``**: image as list of lists of lists of int channel values;
- **``maxcolors``**: maximum of channel value in ``image3d`` list (int),
  255 for 8 bit and 65535 for 16 bit input;
- **``result_file_name``**: name of POV-Ray file to export.

References
----------

.. [1] POV-Ray Documentation, Section 2.4.2.3 `Mesh`_.
.. [2] B1. Object Files (`.obj`_).
.. [3] AutoCAD 2012 `DXF`_ Reference, p. 64.
.. [4] `STL`_ (STereoLithography) File Format, ASCII.
   Sustainability of Digital Formats: Planning for Library of Congress Collections.

.. _Mesh: https://www.povray.org/documentation/view/3.7.1/292/

.. _.obj: https://paulbourke.net/dataformats/obj/obj_spec.pdf

.. _DXF: https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf

.. _STL: https://www.loc.gov/preservation/digital/formats/fdd/fdd000506.shtml

-----
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

img2mesh main Git repositories: `img2mesh@Github`_, `img2mesh@Gitflic`_.

.. _img2mesh@Github: https://github.com/Dnyarri/img2mesh

.. _img2mesh@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh

img2mesh Geometry №1 Git repositories: `img2mesh1@Github`_, `img2mesh1@Gitflic`_.

.. _img2mesh1@Github: https://github.com/Dnyarri/img2mesh/tree/classic

.. _img2mesh1@Gitflic: https://gitflic.ru/project/dnyarri/img2mesh?branch=classic

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2023-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.27.27.7'  # 27 Mar 2026
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from .list2dxf import list2dxf
from .list2obj import list2obj
from .list2pov import list2pov
from .list2stl import list2stl

list2pov = list2pov
list2obj = list2obj
list2stl = list2stl
list2dxf = list2dxf
