
| [〖EN〗](README.md) | 【RU】 |
| ---- | ---- |

# Конвертер из растровых картинок в 3D-сетку треугольников  

Программа на Python для трассировки карты высот в графических форматах [PNG](http://www.libpng.org/pub/png/) или [PGM/PPM](https://dnyarri.github.io/pypnm.html) в трёхмерную векторную сетку треугольников (triangle mesh) в форматах [POVRay](https://www.povray.org/) POV, Wavefront OBJ, Autodesk DXF, а также STL для 3D-принтеров. Координаты x, y пикселя соответствуют координатам x, y узлов сетки, яркость пикселя соответствует высоте (z) узла сетки. В случае исходных графических файлов с низким разрешением полученная при трассировке 3D-сетка обеспечивает лучшее визуальное качество рендеринга, нежели исходные графические файлы при их использовании в качестве heightfield напрямую.  

[![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png "Example of img2mesh output rendering")](https://dnyarri.github.io/img2mesh.html)

## Совместимость с форматами

| Форматы импорта | Форматы экспорта 3D |
| ------ | ------ |
| 16 и 8 бит на канал PNG, PGM и PPM  | POV, OBJ, ASCII STL, ASCII DXF |

## Содержимое

- **img2mesh** - удобный GUI, объединяющий все функции из программ ниже.

- **list2mesh** module, including:

  - **list2pov**: конвертер изображений в сцену POVRay. Полученная сцена содержит 3D-сетку, объект box (CSG intersection), создающий боковые стенки и дно, свет и камеру. Текстуры заявлены в declare отдельно для удобства редактирования;

  - **list2stl**: конвертер изображений в STL. Экспортированный файл содержит 3D-сетку и боковые и нижнюю поверхности в виде сетки, поскольку они необходимы 3D-принтеру;

  - **list2obj**: конвертер изображений в Wavefront OBJ. Экспортированный файл содержит только 3D-сетку;

  - **list2dxf**: конвертер изображений в Autodesk DXF. Экспортированный файл содержит только 3D-сетку;

- Модули **pypng** и **pypnm**, обеспечивающие чтение PNG и PGM/PPM файлов, соответственно.

[![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png "Preview of img2mesh output files in one folder")](https://dnyarri.github.io/img2mesh.html)

## Внешние зависимости

1. [PyPNG](https://gitlab.com/drj11/pypng). Копия включена в дистрибутив img2mesh.
2. [PyPNM](https://pypi.org/project/PyPNM/). Копия включена в дистрибутив img2mesh.
3. Tkinter. Входит в состав типового дистрибутива CPython.

## Installation and Usage

Комплект программ самодостаточен и должен работать сразу после распаковки при наличии на машине стандартной установки Python. Программа оборудована минималистическим GUI, в результате всё, что вы должны сделать после запуска программы, это с помощью кнопки "Open..." выбрать и открыть файл PNG, или PPM, или PGM, затем с помощью кнопки "Export..." выбрать файл для сохранения, подождать, пока программа отработает и закроется, затем открыть полученный файл в подходящей 3D-программе.

### Для разработчиков

Модуль list2mesh, включающий функции 3D-экспорта, может быть свободно использован другими разработчиками.

## Литература

1. [POV-Ray](https://www.povray.org/) и POV SDL.

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf) в [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Cătălin IANCU et al., From CAD model to 3D print via “STL” file format](https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf).

4. [Marshall Burns, Automated Fabrication, Section 6.5](https://www.fabbers.com/tech/STL_Format).

5. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf) by Autodesk, Inc.

### Родственное

[Dnyarri website](https://dnyarri.github.io) - остальной товар от Жабы Огромной Умственной Силы.

[img2mesh с иллюстрациями и объяснениями](https://dnyarri.github.io/img2mesh.html).

[img2mesh source at github](https://github.com/Dnyarri/img2mesh)

[img2mesh source at gitflic mirror](https://gitflic.ru/project/dnyarri/img2mesh)
