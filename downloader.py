"""Автоматическая загрузка Excel-таблиц расписания с сайта ЭлЖур.

Логинится в ЭлЖур, открывает доску объявлений журнала, находит объявления с
расписанием и скачивает приложенные .xlsx в каталог input/.

Файл, приложенный к объявлению, — это готовая книга расписания (лист = параллель),
её и сохраняем без изменений для последующей генерации скриншотов.
"""
from __future__ import annotations

import datetime as dt
import os
import re
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

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
    year = dt.datetime.now(SCHOOL_TZ).year
    return f"{day_month}.{year}"


class ScheduleDownloader:
    def __init__(self, login: str, password: str, base_url: str = "https://fms.eljur.ru", timeout: float = 30.0):
        self.login_name = login
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"User-Agent": USER_AGENT},
            timeout=httpx.Timeout(timeout, connect=10.0),
            follow_redirects=True,
        )

    def login(self) -> bool:
        data = {"username": self.login_name, "password": self.password, "return_uri": "/"}
        try:
            response = self.client.post("/ajaxauthorize", data=data)
        except httpx.HTTPError as exc:
            print(f"Ошибка сети при входе: {exc!r}")
            return False

        if response.status_code != 200:
            print(f"Вход: неожиданный статус {response.status_code}")
            return False

        try:
            result = response.json()
        except ValueError:
            print("Вход: ответ не в формате JSON")
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
    def _extract_download(item) -> Optional[tuple[str, str]]:
        """Возвращает (полная_дата, url_файла) для объявления с расписанием или None."""
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

    def download_all(self, input_dir: str, overwrite: bool = False) -> List[str]:
        """Скачивает все найденные файлы расписания в input_dir. Возвращает пути новых файлов."""
        if not self.login():
            raise RuntimeError("Не удалось войти в ЭлЖур — проверьте логин и пароль.")

        os.makedirs(input_dir, exist_ok=True)
        saved: List[str] = []

        for item in self._board_items():
            extracted = self._extract_download(item)
            if not extracted:
                continue
            full_date, file_url = extracted
            filename = f"{full_date}.xlsx"
            file_path = os.path.join(input_dir, filename)

            if os.path.exists(file_path) and not overwrite:
                print(f"  {filename} — уже есть, пропуск")
                continue

            response = self.client.get(file_url)
            if response.status_code != 200 or not response.content:
                print(f"  {filename} — не удалось скачать (статус {response.status_code})")
                continue

            with open(file_path, "wb") as f:
                f.write(response.content)
            saved.append(file_path)
            print(f"  скачано: {filename}")

        return saved

    def close(self) -> None:
        self.client.close()


def download_schedules(config: dict, input_dir: str, overwrite: bool = False) -> List[str]:
    downloader = ScheduleDownloader(
        login=config["site_login"],
        password=config["site_password"],
        base_url=config.get("site_url") or "https://fms.eljur.ru",
    )
    try:
        return downloader.download_all(input_dir, overwrite=overwrite)
    finally:
        downloader.close()


if __name__ == "__main__":
    from config import load_config, require_credentials

    cfg = load_config()
    require_credentials(cfg)
    print("Загрузка расписаний с сайта...")
    files = download_schedules(cfg, "input")
    print(f"Готово. Новых файлов: {len(files)}")
