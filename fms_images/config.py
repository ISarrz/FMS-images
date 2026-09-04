"""Конфигурация доступа к ЭлЖур."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

from .errors import ConfigError

DEFAULT_SITE_URL = "https://fms.eljur.ru"


@dataclass
class Config:
    """Настройки доступа к сайту ЭлЖур.

    Значения можно задать напрямую, загрузить из JSON-файла (:meth:`from_file`)
    или собрать из файла и переменных окружения (:meth:`load`).
    """

    site_url: str = DEFAULT_SITE_URL
    site_login: Optional[str] = None
    site_password: Optional[str] = None

    @classmethod
    def from_file(cls, path: str = "config.json") -> "Config":
        """Читает конфиг из JSON-файла. Отсутствующий файл даёт конфиг по умолчанию."""
        data = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        return cls(
            site_url=data.get("site_url") or DEFAULT_SITE_URL,
            site_login=data.get("site_login"),
            site_password=data.get("site_password"),
        )

    @classmethod
    def from_env(cls, base: Optional["Config"] = None) -> "Config":
        """Накладывает переменные окружения поверх ``base`` (или конфига по умолчанию)."""
        base = base or cls()
        return cls(
            site_url=os.environ.get("FMS_ELJUR_URL", base.site_url) or DEFAULT_SITE_URL,
            site_login=os.environ.get("FMS_ELJUR_LOGIN", base.site_login),
            site_password=os.environ.get("FMS_ELJUR_PASSWORD", base.site_password),
        )

    @classmethod
    def load(cls, path: str = "config.json", use_env: bool = True) -> "Config":
        """Загружает конфиг из файла, затем (по умолчанию) применяет переменные окружения."""
        config = cls.from_file(path)
        if use_env:
            config = cls.from_env(config)
        return config

    @property
    def has_credentials(self) -> bool:
        return bool(self.site_login and self.site_password)

    def require_credentials(self) -> None:
        """Бросает :class:`ConfigError`, если логин/пароль не заданы."""
        if not self.has_credentials:
            raise ConfigError(
                "Не заданы логин/пароль ЭлЖур. Заполните config.json "
                "или задайте переменные FMS_ELJUR_LOGIN и FMS_ELJUR_PASSWORD."
            )
