
| [EN](README.md) | 『✅RU』 |
| ---- | ---- |

# Конвертер из растровых картинок в 3D-сетку треугольников  

Программа на Python для трассировки карты высот в графическом формате ([PNG](http://www.libpng.org/pub/png/)) в трёхмерную векторную сетку треугольников (triangle mesh) в форматах [POVRay](https://www.povray.org/) POV, Wavefront OBJ, Autodesk DXF, а также STL для 3D-принтеров. Координаты x, y пикселя соответствуют координатам x, y узлов сетки, яркость пикселя соответствует высоте (z) узла сетки. В случае исходных графических файлов с низким разрешением полученная при трассировке 3D-сетка обеспечивает лучшее визуальное качество рендеринга, нежели исходные графические файлы при их использовании в качестве heightfield напрямую.  

[![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png)](https://dnyarri.github.io/img2mesh.html)

## Содержимое

- **img2mesh** - удобный GUI, объединяющий все функции из программ ниже.

- **img2pov** - конвертер изображений в сцену POVRay. Полученная сцена содержит 3D-сетку, объект box (CSG intersection), создающий боковые стенки и дно, свет и камеру. Текстуры заявлены в declare отдельно для удобства редактирования.

- **img2obj** - конвертер изображений в Wavefront OBJ. Экспортированный файл содержит только 3D-сетку.

- **img2dxf** - конвертер изображений в Autodesk DXF. Экспортированный файл содержит только 3D-сетку.

- **img2stl** - конвертер изображений в STL. Экспортированный файл содержит 3D-сетку и боковые и нижнюю поверхности в виде сетки, поскольку они необходимы 3D-принтеру.

[![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png)](https://dnyarri.github.io/img2mesh.html)

## Внешние зависимости

1. [PyPNG](https://gitlab.com/drj11/pypng). Копия включена в дистрибутив img2mesh.
2. [PyPNM](https://pypi.org/project/PyPNM/). Копия включена в дистрибутив img2mesh.
3. Tkinter. Входит в состав типового дистрибутива CPython.

## Installation and Usage

Комплект программ самодостаточен и должен работать сразу после распаковки при наличии на машине Python. Программы оборудованы минималистическим GUI, в результате всё, что вы должны сделать после запуска программы, это с помощью окна "Open..." выбрать и открыть файл PNG, или PPM, или PGM, затем с помощью окна "Save..." выбрать файл для сохранения, подождать, пока программа отработает и закроется, затем открыть полученный файл в подходящей 3D-программе.

### Для разработчиков

Модуль list2mesh, включающий функции 3D-экспорта, может быть свободно использован другими разработчиками.

## Литература

1. [POV-Ray](https://www.povray.org/) и POV SDL.

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf) в [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Stereo Lithography Files (.stl)](https://paulbourke.net/dataformats/stl/) [*ibid*](https://paulbourke.net/dataformats/).

4. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf) от Autodesk, Inc.

### Родственное

[Dnyarri website](https://dnyarri.github.io) - остальной товар от Жабы Огромной Умственной Силы.

[github Dnyarri](https://github.com/Dnyarri/img2mesh).

[gitflic Dnyarri](https://gitflic.ru/project/dnyarri/img2mesh).
