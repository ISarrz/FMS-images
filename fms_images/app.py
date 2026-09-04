"""Высокоуровневый фасад: загрузка + генерация в одном объекте."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .config import Config
from .downloader import download_schedules
from .renderer import DEFAULT_DPI, RenderTools, render_directory

DEFAULT_INPUT_DIR = "data/input"
DEFAULT_OUTPUT_DIR = "data/output"


@dataclass
class ScheduleImages:
    """Связывает настройки и каталоги, предоставляя методы загрузки и рендеринга.

    Пример::

        from fms_images import ScheduleImages, Config

        app = ScheduleImages(config=Config.load())
        app.download()          # скачать .xlsx с ЭлЖур в data/input
        images = app.render()   # data/output/<дата>/<параллель>.png
        # или всё сразу:
        images = app.run()
    """

    config: Config = field(default_factory=Config)
    input_dir: str = DEFAULT_INPUT_DIR
    output_dir: str = DEFAULT_OUTPUT_DIR
    dpi: int = DEFAULT_DPI
    tools: Optional[RenderTools] = None

    def download(self, overwrite: bool = False) -> List[Path]:
        """Скачивает расписания с сайта в ``input_dir``."""
        return download_schedules(self.config, self.input_dir, overwrite=overwrite)

    def render(self) -> List[Path]:
        """Генерирует PNG из всех .xlsx в ``input_dir`` в ``output_dir``."""
        tools = self.tools or RenderTools.discover()
        return render_directory(self.input_dir, self.output_dir, dpi=self.dpi, tools=tools)

    def run(self, overwrite: bool = False) -> List[Path]:
        """Скачивает свежие расписания, затем генерирует изображения."""
        self.download(overwrite=overwrite)
        return self.render()
