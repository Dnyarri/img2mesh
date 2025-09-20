
| [〖EN〗](README.md) | 【RU】 |
| ---- | ---- |

# Конвертер из растровых картинок в 3D-сетку треугольников  

Программа на Python для трассировки карты высот в графических форматах [PNG](http://www.libpng.org/pub/png/) или [PGM/PPM](https://dnyarri.github.io/pypnm.html) в трёхмерную векторную сетку треугольников (triangle mesh) в форматах [POV-Ray](https://www.povray.org/) POV, Wavefront OBJ, Autodesk DXF, а также STL для 3D-принтеров. Координаты x, y пикселя соответствуют координатам x, y узлов сетки, яркость пикселя соответствует высоте (z) узла сетки. В случае исходных графических файлов с низким разрешением полученная при трассировке 3D-сетка обеспечивает лучшее визуальное качество рендеринга, нежели исходные графические файлы при их использовании в качестве heightfield напрямую.  

[![Example of img2mesh output rendering](https://dnyarri.github.io/imgmesh/640/img2mesh.png "Example of img2mesh output rendering")](https://dnyarri.github.io/img2mesh.html)

## Совместимость с форматами

| Форматы импорта | Форматы экспорта 3D |
| ------ | ------ |
| 16 и 8 бит на канал PNG, PGM и PPM  | POV, OBJ, ASCII STL, ASCII DXF |

## Содержимое

- **img2mesh** - удобный GUI, объединяющий все функции из программ ниже.

- **list2mesh** module, including:

  - **list2pov**: конвертер изображений в сцену POV-Ray. Полученная сцена содержит 3D-сетку, объект box (CSG intersection), создающий боковые стенки и дно, свет и камеру. Текстуры заявлены в declare отдельно для удобства редактирования;

  - **list2stl**: конвертер изображений в STL. Экспортированный файл содержит 3D-сетку и боковые и нижнюю поверхности в виде сетки, поскольку они необходимы 3D-принтеру;

  - **list2obj**: конвертер изображений в Wavefront OBJ. Экспортированный файл содержит только 3D-сетку;

  - **list2dxf**: конвертер изображений в Autodesk DXF. Экспортированный файл содержит только 3D-сетку;

- Модули **pypng** и **pypnm**, обеспечивающие чтение PNG и PGM/PPM файлов, соответственно.

[![Preview of img2mesh output files in one folder](https://dnyarri.github.io/imgmesh/printscreen.png "Preview of img2mesh output files in one folder")](https://dnyarri.github.io/img2mesh.html)

## Необходимые исходные и Внешние зависимости

1. [Python](https://www.python.org/) 3.11 или посвежее.
2. [PyPNG](https://gitlab.com/drj11/pypng). Копия включена в дистрибутив img2mesh.
3. [PyPNM](https://pypi.org/project/PyPNM/). Копия включена в дистрибутив img2mesh.
4. Tkinter. Обыкновенно входит в состав типового дистрибутива CPython.

> [!NOTE]
> Начиная с img2mesh 3.21.2.16 PyPNM, включённый в дистрибутив, обновлён до [PyPNM "Victory 2" main](https://github.com/Dnyarri/PyPNM), предназначенный для работы под Python 3.11 и выше. Единственное практическое ограничение совместимости - данная версия не содержит трюков для отображения 16 bpc картинок под старым Tkinter, включённым в старый CPython. Если вам хочется вернуть назад совместимость со старым TKinter, вы можете скачать руками [PyPNM extended compatibility version](https://github.com/Dnyarri/PyPNM/tree/py34) и вставить его на место нового PyPNM тем же местом (то есть руками).

## Развёртывание и боевое применение

Комплект программ самодостаточен и должен работать сразу после распаковки при наличии на машине стандартной установки CPython. Программа оборудована минималистическим GUI, в результате всё, что вы должны сделать после запуска программы, это с помощью двойного клика в диалог или Ctrl+O запустить "Open...", выбрать и открыть файл PNG, или PPM, или PGM, затем с помощью правого клика или Alt+F вызвать меню "File" и выбрать файл для сохранения, подождать, пока программа отработает и закроется, затем открыть полученный файл в подходящей 3D-программе.

### Для разработчиков

Модуль экспорта, включающий функции 3D-экспорта, может быть использован другими разработчиками безвозмездно, то есть даром.

## Литература

1. [POV-Ray](https://www.povray.org/) и [спецификция POV SDL](https://www.povray.org/documentation/3.7.0/).

2. [Wavefront Object Files (.obj)](https://paulbourke.net/dataformats/obj/obj_spec.pdf) в [Paul Bourke collection](https://paulbourke.net/dataformats/).

3. [Cătălin IANCU et al., From CAD model to 3D print via “STL” file format](https://www.utgjiu.ro/rev_mec/mecanica/pdf/2010-01/13_Catalin%20Iancu.pdf).

4. [Marshall Burns, Automated Fabrication, Section 6.5](https://www.fabbers.com/tech/STL_Format).

5. [DXF Reference](https://images.autodesk.com/adsk/files/autocad_2012_pdf_dxf-reference_enu.pdf) by Autodesk, Inc.

### Родственное

[Dnyarri website](https://dnyarri.github.io) - остальной питонистый навар, отставить, товар от Жабы Огромной Умственной Силы.

[img2mesh с иллюстрациями и объяснениями](https://dnyarri.github.io/img2mesh.html).

[img2mesh source at github](https://github.com/Dnyarri/img2mesh)

[img2mesh source at gitflic mirror](https://gitflic.ru/project/dnyarri/img2mesh)
