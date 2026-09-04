"""Исключения библиотеки fms_images."""


class FmsImagesError(Exception):
    """Базовое исключение библиотеки."""


class ConfigError(FmsImagesError):
    """Некорректная или неполная конфигурация (нет логина/пароля и т.п.)."""


class DependencyError(FmsImagesError):
    """Отсутствует внешняя зависимость (libreoffice/soffice, pdftoppm)."""


class RenderError(FmsImagesError):
    """Ошибка при конвертации Excel в изображение."""


class LoginError(FmsImagesError):
    """Не удалось войти в ЭлЖур."""
