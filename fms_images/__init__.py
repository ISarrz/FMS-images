"""fms_images — загрузка расписаний с ЭлЖур и генерация PNG-скриншотов по параллелям.

Основной публичный API::

    from fms_images import (
        Config, ScheduleImages,
        ScheduleDownloader, download_schedules,
        render_workbook, render_directory, RenderTools,
    )
"""
from __future__ import annotations

import logging

from .app import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, ScheduleImages
from .config import Config
from .downloader import ScheduleDownloader, download_schedules
from .errors import (
    ConfigError,
    DependencyError,
    FmsImagesError,
    LoginError,
    RenderError,
)
from .renderer import (
    DEFAULT_DPI,
    RenderTools,
    iter_workbooks,
    render_directory,
    render_workbook,
)

# библиотека не навязывает вывод логов
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.1.0"

__all__ = [
    "Config",
    "ScheduleImages",
    "ScheduleDownloader",
    "download_schedules",
    "render_workbook",
    "render_directory",
    "iter_workbooks",
    "RenderTools",
    "DEFAULT_DPI",
    "DEFAULT_INPUT_DIR",
    "DEFAULT_OUTPUT_DIR",
    "FmsImagesError",
    "ConfigError",
    "DependencyError",
    "RenderError",
    "LoginError",
    "__version__",
]
