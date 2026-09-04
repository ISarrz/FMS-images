# FMS-images

Python-библиотека для **загрузки расписаний с ЭлЖур** и генерации **настоящих
PNG-скриншотов** Excel-таблиц — по одному изображению на каждую **параллель**.

В книге `.xlsx` каждый лист соответствует одной параллели (например, `10`, `11`).
Библиотека рендерит **сами листы Excel «как есть»** — с их родным оформлением
(цвета, границы, шрифты) — через LibreOffice, ничего не перерисовывая вручную.
Скриншоты одной книги складываются в отдельную папку по её имени.

## Установка

Системные пакеты (Fedora):

```bash
sudo dnf install libreoffice-calc poppler-utils
```

Пакет:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .          # установит fms_images и консольную команду fms-images
```

## Использование как библиотеки

Высокоуровневый фасад:

```python
from fms_images import ScheduleImages, Config

app = ScheduleImages(config=Config.load())   # config.json / переменные окружения
app.download()                               # скачать .xlsx в data/input
images = app.render()                        # data/output/<дата>/<параллель>.png
# либо всё сразу:
images = app.run()
```

Отдельные функции:

```python
from fms_images import (
    Config, download_schedules,
    render_workbook, render_directory, RenderTools,
)

cfg = Config.load()
download_schedules(cfg, "data/input")                 # только загрузка
render_workbook("data/input/05.09.2026.xlsx", "data/output")  # одна книга
render_directory("data/input", "data/output", dpi=200)        # все книги
```

Всё, что печатается, идёт через модуль `logging` — библиотека сама ничего не
выводит и не завершает процесс; ошибки — это исключения (`FmsImagesError` и
подклассы: `ConfigError`, `DependencyError`, `RenderError`, `LoginError`).

## Использование как CLI (необязательно)

```bash
fms-images --download            # скачать и сгенерировать (или: python -m fms_images)
fms-images --download --overwrite
fms-images                       # только генерация из data/input
fms-images data/input/05.09.2026.xlsx
fms-images --input-dir data/input --output-dir data/output --dpi 200
```

## Настройка доступа к ЭлЖур

```bash
cp config.example.json config.json   # затем впишите логин и пароль
```

`config.json` в репозиторий не попадает. Вместо файла можно задать переменные
окружения `FMS_ELJUR_LOGIN`, `FMS_ELJUR_PASSWORD` (и при необходимости
`FMS_ELJUR_URL`) — они имеют приоритет.

## Как это работает

```
ЭлЖур  ──►  .xlsx      логин, доска объявлений -> скачивание в data/input/
.xlsx  ──►  PDF        LibreOffice (headless), каждый лист = отдельная страница
       ──►  PNG        pdftoppm (poppler), одна страница = один лист-параллель
       ──►  обрезка    Pillow убирает белые поля
```

## Структура

```
FMS-images/
├── fms_images/            # пакет
│   ├── app.py             # фасад ScheduleImages
│   ├── config.py          # Config (config.json / переменные окружения)
│   ├── downloader.py      # ScheduleDownloader, download_schedules
│   ├── renderer.py        # render_workbook, render_directory, RenderTools
│   ├── errors.py          # иерархия исключений
│   └── cli.py             # тонкий CLI (fms-images / python -m fms_images)
├── data/
│   ├── input/             # исходные .xlsx
│   └── output/<дата>/     # PNG по параллелям (папка на каждую книгу)
├── config.example.json
├── pyproject.toml
└── README.md
```

Пример результата (`data/output/05.09.2026/10.png`):

![Расписание 10-х классов](data/output/05.09.2026/10.png)

## Примечание

Пример в `data/` содержит реальное школьное расписание с фамилиями учителей —
приведён как демонстрация работы.
