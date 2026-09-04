"""
FMS-images — генерация PNG-скриншотов расписания уроков из Excel.

Каждый лист книги (.xlsx) — это отдельная параллель (например, «10», «11»).
Скрипт читает каждый лист, учитывает объединённые ячейки и многострочные
значения и сохраняет по одному PNG на параллель в каталог output/.

Использование:
    python generate.py                      # обработать все .xlsx из input/
    python generate.py input/05.09.2026.xlsx
    python generate.py path/to/file.xlsx --input-dir input --output-dir output

Рендеринг выполняется пакетом painter (перенесён из проекта FMS-bot).
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

import openpyxl
from openpyxl.utils import get_column_letter
from PIL import Image, ImageDraw

from painter import Table, Text, colors

# --- Параметры оформления -------------------------------------------------

BACKGROUND = colors["discord4"]        # цвет фона всего изображения
HEADER_FILL = colors["discord3"]       # заголовки (шапка / левый столбец)
BODY_FILL = colors["discord1"]         # ячейки с уроками
OUTLINE_COLOR = colors["discord2"]     # цвет линий сетки
TEXT_COLOR = "white"

HEADER_ROWS = 3      # первые N строк листа считаем шапкой
HEADER_COLS = 3      # первые N столбцов (день/№/время) считаем шапкой
MAX_LINE_LENGTH = 22  # мягкий перенос длинных слов/строк в ячейке

MARGIN = 20          # поля изображения вокруг таблицы


def _wrap_line(line: str, max_length: int = MAX_LINE_LENGTH) -> List[str]:
    """Перенос одной строки по словам, чтобы ячейки не были слишком широкими."""
    words = line.split()
    if not words:
        return [""]

    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_length:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def normalize_value(value: str) -> str:
    """Нормализует текст ячейки: сохраняет исходные переносы и мягко переносит длинные строки."""
    result: List[str] = []
    for raw_line in str(value).split("\n"):
        result.extend(_wrap_line(raw_line.strip()))
    return "\n".join(result)


def _is_header(row: int, column: int) -> bool:
    return row < HEADER_ROWS or column < HEADER_COLS


def build_table(sheet) -> Optional[Table]:
    """Строит painter.Table из листа Excel. Возвращает None для пустого листа."""
    height = sheet.max_row
    width = sheet.max_column
    if not height or not width:
        return None

    content: List[List[None]] = [[None for _ in range(width)] for _ in range(height)]
    table = Table(content=content, left_top=(MARGIN, MARGIN))

    has_text = False
    for row in range(height):
        for column in range(width):
            value = sheet.cell(row=row + 1, column=column + 1).value
            if value is None or str(value).strip() == "":
                continue
            has_text = True
            is_header = _is_header(row, column)
            table[row][column].content = Text(
                value=normalize_value(value),
                font="Roboto Black" if is_header else "Roboto Bold",
                size=30 if is_header else 26,
                fill=TEXT_COLOR,
            )

    if not has_text:
        return None

    _apply_merges(table, sheet, height, width)
    _style_table(table, height, width)
    return table


def _apply_merges(table: Table, sheet, height: int, width: int) -> None:
    """Переносит объединённые диапазоны Excel в таблицу painter.

    Диапазон объединяется в два прохода: сначала вертикальные полосы по каждому
    столбцу, затем полосы соединяются по горизонтали — так объединяются только
    соседние блоки, что и ожидает painter.
    """
    for cell_range in sheet.merged_cells.ranges:
        r0 = cell_range.min_row - 1
        r1 = cell_range.max_row - 1
        c0 = cell_range.min_col - 1
        c1 = cell_range.max_col - 1

        # ограничиваемся фактическими размерами таблицы
        r1 = min(r1, height - 1)
        c1 = min(c1, width - 1)
        if r0 > r1 or c0 > c1 or (r0 == r1 and c0 == c1):
            continue

        # вертикальные полосы по каждому столбцу диапазона
        for column in range(c0, c1 + 1):
            for row in range(r0, r1):
                table.unite_cells((r0, column), (row + 1, column))

        # соединяем полосы по горизонтали
        for column in range(c0, c1):
            table.unite_cells((r0, c0), (r0, column + 1))


def _style_table(table: Table, height: int, width: int) -> None:
    """Задаёт заливку, сетку, отступы и выравнивание ячеек."""
    for row in range(height):
        for column in range(width):
            cell = table[row][column]
            # пропускаем «поглощённые» части объединённых ячеек
            if not table._cell_is_active(cell):
                continue

            if cell.content is None:
                # пустая ячейка — сливается с фоном, без рамки
                cell.fill = BACKGROUND
                cell.outline_width = 0
                cell.pixels.padding = 0
                continue

            cell.fill = HEADER_FILL if _is_header(row, column) else BODY_FILL
            cell.outline_color = OUTLINE_COLOR
            cell.outline_width = 4
            cell.pixels.padding = 14
            cell.horizontal_alignment = "center"
            cell.vertical_alignment = "center"
            if cell.content is not None:
                cell.content.horizontal_alignment = "center"

    table.squeeze()


def render_sheet_to_png(sheet, out_path: str) -> bool:
    """Рендерит один лист в PNG. Возвращает True, если файл сохранён."""
    table = build_table(sheet)
    if table is None:
        return False

    image = Image.new(
        "RGB",
        (table.pixels.width + 2 * MARGIN, table.pixels.height + 2 * MARGIN),
        BACKGROUND,
    )
    canvas = ImageDraw.Draw(image)
    table.draw(canvas)
    image.save(out_path, format="PNG")
    return True


def process_workbook(xlsx_path: str, output_dir: str) -> List[str]:
    """Обрабатывает книгу: по одному PNG на лист-параллель. Возвращает пути к файлам."""
    workbook = openpyxl.load_workbook(xlsx_path, data_only=True)
    base = os.path.splitext(os.path.basename(xlsx_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    saved: List[str] = []
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        safe_name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in sheet_name)
        out_path = os.path.join(output_dir, f"{base}_{safe_name}.png")
        if render_sheet_to_png(sheet, out_path):
            saved.append(out_path)
            print(f"  параллель {sheet_name!r:>6} -> {out_path}")
        else:
            print(f"  параллель {sheet_name!r:>6} — пусто, пропущено")
    return saved


def collect_inputs(args) -> List[str]:
    if args.files:
        return args.files
    if not os.path.isdir(args.input_dir):
        return []
    return sorted(
        os.path.join(args.input_dir, name)
        for name in os.listdir(args.input_dir)
        if name.lower().endswith(".xlsx") and not name.startswith("~$")
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Генерация PNG-скриншотов расписания из Excel по параллелям (листам)."
    )
    parser.add_argument("files", nargs="*", help="конкретные .xlsx (по умолчанию — все из --input-dir)")
    parser.add_argument("--input-dir", default="input", help="каталог с .xlsx (по умолчанию: input)")
    parser.add_argument("--output-dir", default="output", help="куда сохранять PNG (по умолчанию: output)")
    args = parser.parse_args()

    inputs = collect_inputs(args)
    if not inputs:
        print("Не найдено ни одного .xlsx. Положите файлы в каталог input/ или укажите путь явно.")
        return 1

    total = 0
    for xlsx_path in inputs:
        if not os.path.isfile(xlsx_path):
            print(f"Файл не найден: {xlsx_path}")
            continue
        print(f"Обрабатываю {xlsx_path}")
        total += len(process_workbook(xlsx_path, args.output_dir))

    print(f"Готово. Сохранено изображений: {total}")
    return 0 if total else 1


if __name__ == "__main__":
    sys.exit(main())
