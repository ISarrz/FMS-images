"""Загрузка Excel-таблиц расписания с сайта ЭлЖур."""
from __future__ import annotations

import datetime as dt
import logging
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

from .config import Config
from .errors import LoginError

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115 Safari/537.36"
# Красноярск, GMT+7 — как в исходном проекте FMS-bot
SCHOOL_TZ = dt.timezone(dt.timedelta(hours=7))


def _candidate_dates() -> List[str]:
    """Полные даты (DD.MM.YYYY) для прошлой, текущей и следующей недели."""
    now = dt.datetime.now(SCHOOL_TZ)
    monday = now - dt.timedelta(days=now.weekday())
    result: List[str] = []
    for week_offset in (-7, 0, 7):
        week_monday = monday + dt.timedelta(days=week_offset)
        for day in range(7):
            result.append((week_monday + dt.timedelta(days=day)).strftime("%d.%m.%Y"))
    return result


def _full_date_for(day_month: str) -> str:
    """Достраивает DD.MM до DD.MM.YYYY, подбирая корректный год из окна недель."""
    for full in _candidate_dates():
        if full.startswith(day_month + "."):
            return full
    return f"{day_month}.{dt.datetime.now(SCHOOL_TZ).year}"


class ScheduleDownloader:
    """Клиент ЭлЖур: вход и скачивание файлов расписания с доски объявлений."""

    def __init__(
        self,
        login: str,
        password: str,
        base_url: str = "https://fms.eljur.ru",
        timeout: float = 30.0,
    ):
        self.login_name = login
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(timeout, connect=10.0),
            follow_redirects=True,
        )

    @classmethod
    def from_config(cls, config: Config, timeout: float = 30.0) -> "ScheduleDownloader":
        config.require_credentials()
        return cls(config.site_login, config.site_password, config.site_url, timeout=timeout)

    # -- контекстный менеджер -------------------------------------------------
    def __enter__(self) -> "ScheduleDownloader":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self.client.close()

    # -- сеть -----------------------------------------------------------------
    def login(self) -> bool:
        """Выполняет вход. Возвращает True при успехе."""
        data = {"username": self.login_name, "password": self.password, "return_uri": "/"}
        try:
            response = self.client.post("/ajaxauthorize", data=data)
        except httpx.HTTPError as exc:
            logger.error("ошибка сети при входе: %r", exc)
            return False

        if response.status_code != 200:
            logger.error("вход: неожиданный статус %s", response.status_code)
            return False

        try:
            result = response.json()
        except ValueError:
            logger.error("вход: ответ не в формате JSON")
            return False

        actions = result.get("actions") or []
        if not result.get("result") or not actions:
            return False
        return actions[0].get("type") == "redirect"

    def _board_items(self):
        response = self.client.get("/journal-board-action")
        soup = BeautifulSoup(response.text, "lxml")
        return soup.find_all(class_="board-item")

    @staticmethod
    def _extract_download(item) -> Optional[Tuple[str, str]]:
        """Возвращает (полная_дата, url) для объявления с расписанием или None."""
        title_el = item.find(class_="board-item__title")
        if not title_el:
            return None
        title = title_el.text.strip().lower()
        if "расписание" not in title or "спец" in title or "клуб" in title:
            return None

        button = item.find("a", class_="button button--outline button--purple")
        if not button:
            return None
        button_title = button.find(class_="button__title")
        if not button_title:
            return None

        match = re.search(r"\b\d{2}\.\d{2}\b", button_title.text.strip())
        if not match:
            return None

        file_url = button.attrs.get("href")
        if not file_url:
            return None

        return _full_date_for(match.group()), file_url

    def download_all(self, input_dir: str, overwrite: bool = False) -> List[Path]:
        """Скачивает все найденные файлы расписания в ``input_dir``.

        :raises LoginError: если не удалось войти.
        :returns: пути к вновь скачанным файлам.
        """
        if not self.login():
            raise LoginError("Не удалось войти в ЭлЖур — проверьте логин и пароль.")

        os.makedirs(input_dir, exist_ok=True)
        saved: List[Path] = []

        for item in self._board_items():
            extracted = self._extract_download(item)
            if not extracted:
                continue
            full_date, file_url = extracted
            file_path = Path(input_dir) / f"{full_date}.xlsx"

            if file_path.exists() and not overwrite:
                logger.info("%s — уже есть, пропуск", file_path.name)
                continue

            response = self.client.get(file_url)
            if response.status_code != 200 or not response.content:
                logger.warning("%s — не удалось скачать (статус %s)", file_path.name, response.status_code)
                continue

            file_path.write_bytes(response.content)
            saved.append(file_path)
            logger.info("скачано: %s", file_path.name)

        return saved


def download_schedules(
    config: Config,
    input_dir: str,
    *,
    overwrite: bool = False,
    timeout: float = 30.0,
) -> List[Path]:
    """Удобная обёртка: скачивает расписания по настройкам ``config`` в ``input_dir``."""
    with ScheduleDownloader.from_config(config, timeout=timeout) as downloader:
        return downloader.download_all(input_dir, overwrite=overwrite)
