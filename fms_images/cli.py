"""Тонкий CLI поверх библиотеки fms_images (необязательный способ запуска)."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import List, Optional

from .app import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, ScheduleImages
from .config import Config
from .errors import FmsImagesError
from .renderer import DEFAULT_DPI, RenderTools, render_directory, render_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fms-images",
        description="Скачивание расписаний с ЭлЖур и генерация PNG-скриншотов по параллелям.",
    )
    parser.add_argument("files", nargs="*", help="конкретные .xlsx (по умолчанию — все из --input-dir)")
    parser.add_argument("--input-dir", default=DEFAULT_INPUT_DIR, help=f"каталог с .xlsx (по умолчанию: {DEFAULT_INPUT_DIR})")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"куда сохранять PNG (по умолчанию: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"разрешение рендеринга (по умолчанию: {DEFAULT_DPI})")
    parser.add_argument("--download", action="store_true", help="сначала скачать актуальные расписания с ЭлЖур")
    parser.add_argument("--overwrite", action="store_true", help="перезаписывать уже скачанные файлы (с --download)")
    parser.add_argument("--config", default="config.json", help="путь к config.json (с --download)")
    parser.add_argument("-q", "--quiet", action="store_true", help="меньше сообщений")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(message)s",
    )

    try:
        tools = RenderTools.discover()

        if args.download:
            config = Config.load(args.config)
            config.require_credentials()
            logging.info("Загрузка расписаний с сайта ЭлЖур...")
            downloaded = ScheduleImages(
                config=config, input_dir=args.input_dir, output_dir=args.output_dir,
            ).download(overwrite=args.overwrite)
            logging.info("Новых файлов: %d", len(downloaded))

        if args.files:
            images = []
            for path in args.files:
                images.extend(render_workbook(path, args.output_dir, dpi=args.dpi, tools=tools))
        else:
            images = render_directory(args.input_dir, args.output_dir, dpi=args.dpi, tools=tools)

    except FmsImagesError as exc:
        logging.error("%s", exc)
        return 1

    logging.info("Готово. Сохранено изображений: %d", len(images))
    return 0 if images else 1


if __name__ == "__main__":
    sys.exit(main())
