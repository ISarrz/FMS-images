"""Загрузка настроек: доступ к ЭлЖур и адрес сайта.

Значения берутся из config.json (не хранится в git) и/или переменных окружения.
Переменные окружения имеют приоритет над config.json:

    FMS_ELJUR_URL       адрес сайта (по умолчанию https://fms.eljur.ru)
    FMS_ELJUR_LOGIN     логин
    FMS_ELJUR_PASSWORD  пароль
"""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

DEFAULTS: Dict[str, Optional[str]] = {
    "site_url": "https://fms.eljur.ru",
    "site_login": None,
    "site_password": None,
}


def load_config(path: str = "config.json") -> Dict[str, Optional[str]]:
    config = dict(DEFAULTS)

    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            config.update(json.load(f))

    config["site_url"] = os.environ.get("FMS_ELJUR_URL", config["site_url"]) or DEFAULTS["site_url"]
    config["site_login"] = os.environ.get("FMS_ELJUR_LOGIN", config["site_login"])
    config["site_password"] = os.environ.get("FMS_ELJUR_PASSWORD", config["site_password"])
    return config


def require_credentials(config: Dict[str, Optional[str]]) -> None:
    if not config.get("site_login") or not config.get("site_password"):
        raise SystemExit(
            "Не заданы логин/пароль ЭлЖур.\n"
            "Скопируйте config.example.json в config.json и заполните его,\n"
            "либо задайте переменные FMS_ELJUR_LOGIN и FMS_ELJUR_PASSWORD."
        )
