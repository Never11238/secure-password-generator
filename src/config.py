"""Модуль конфигурации проекта."""

import os
import copy
import logging
from pathlib import Path
from typing import Any, Dict

# TOML парсер: stdlib в 3.11+, fallback tomli для старых версий
try:
    import tomllib  # type: ignore  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore  # fallback для <3.11

logger = logging.getLogger(__name__)

# Константы
CONFIG_FILENAME = ".passgen.toml"
DEFAULTS: Dict[str, Any] = {
    "random": {
        "length": 16,
        "min_length": 8,
        "max_length": 64,
        "include_lowercase": True,
        "include_uppercase": True,
        "include_digits": True,
        "include_symbols": True,
        "exclude_ambiguous": False,
        "require_all_types": False,
        "min_entropy": 60,
    },
    "passphrase": {
        "words": 4,
        "min_words": 3,
        "max_words": 8,
        "separator": "-",
        "capitalize": False,
        "add_number": True,
    },
    "security": {
        "enable_blacklist": True,
        "blacklist_path": None,
        "check_duplicates": True,
        "history_size": 100,
    },
    "logging": {
        "level": "INFO",
        "file": None,
        "enable_generation_log": True,
    },
    "gui": {
        "theme": "System",
        "color_theme": "blue",
        "auto_copy": False,
        "auto_clear_clipboard": 30,
    },
}


def get_config_path() -> Path:
    """Вернуть путь к файлу конфигурации пользователя."""
    return Path.home() / CONFIG_FILENAME


def _safe_load_toml(filepath: Path) -> Dict[str, Any]:
    """Безопасно загрузить TOML файл, возвращая пустой dict при ошибке."""
    if not filepath.exists():
        return {}
    try:
        with open(filepath, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config from {filepath}: {e}")
        return {}


def load_config() -> Dict[str, Any]:
    """
    Загрузить конфигурацию: дефолты + файл пользователя.

    Returns:
        Словарь с объединённой конфигурацией.
    """
    # Глубокая копия дефолтов (чтобы не мутировать глобальную константу)
    config = copy.deepcopy(DEFAULTS)

    # Загрузить пользовательский конфиг
    config_path = get_config_path()
    file_config = _safe_load_toml(config_path)

    # Слияние: значения из file_config перезаписывают дефолты
    # Рекурсивно для вложенных словарей
    def _merge_dicts(base: Dict, override: Dict) -> None:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                _merge_dicts(base[key], value)
            else:
                base[key] = value

    _merge_dicts(config, file_config)

    logger.debug(f"Config loaded from {config_path}")
    return config


def create_default_config(overwrite: bool = False) -> bool:
    """
    Создать файл конфигурации по умолчанию.

    Args:
        overwrite: Перезаписать существующий файл.

    Returns:
        True если файл создан, False если уже существует.
    """
    config_path = get_config_path()

    if config_path.exists() and not overwrite:
        logger.info(f"Config already exists: {config_path}")
        return False

    try:
        # Создаём родительские директории если нужно
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Записываем конфиг в формате TOML (упрощённо, вручную)
        # Для полноценной записи можно использовать 'tomli-w' или 'tomlkit'
        lines = [
            "# Secure Password Generator Configuration",
            "# Generated automatically. Edit with care.",
            "",
            "[random]",
            f"length = {DEFAULTS['random']['length']}",
            f"min_length = {DEFAULTS['random']['min_length']}",
            f"max_length = {DEFAULTS['random']['max_length']}",
            f"include_lowercase = {str(DEFAULTS['random']['include_lowercase']).lower()}",
            f"include_uppercase = {str(DEFAULTS['random']['include_uppercase']).lower()}",
            f"include_digits = {str(DEFAULTS['random']['include_digits']).lower()}",
            f"include_symbols = {str(DEFAULTS['random']['include_symbols']).lower()}",
            f"exclude_ambiguous = {str(DEFAULTS['random']['exclude_ambiguous']).lower()}",
            f"require_all_types = {str(DEFAULTS['random']['require_all_types']).lower()}",
            f"min_entropy = {DEFAULTS['random']['min_entropy']}",
            "",
            "[passphrase]",
            f"words = {DEFAULTS['passphrase']['words']}",
            f"min_words = {DEFAULTS['passphrase']['min_words']}",
            f"max_words = {DEFAULTS['passphrase']['max_words']}",
            f"separator = \"{DEFAULTS['passphrase']['separator']}\"",
            f"capitalize = {str(DEFAULTS['passphrase']['capitalize']).lower()}",
            f"add_number = {str(DEFAULTS['passphrase']['add_number']).lower()}",
            "",
            "[security]",
            f"enable_blacklist = {str(DEFAULTS['security']['enable_blacklist']).lower()}",
            f"check_duplicates = {str(DEFAULTS['security']['check_duplicates']).lower()}",
            f"history_size = {DEFAULTS['security']['history_size']}",
            "",
            "[logging]",
            f"level = \"{DEFAULTS['logging']['level']}\"",
            f"enable_generation_log = {str(DEFAULTS['logging']['enable_generation_log']).lower()}",
            "",
            "[gui]",
            f"theme = \"{DEFAULTS['gui']['theme']}\"",
            f"color_theme = \"{DEFAULTS['gui']['color_theme']}\"",
            f"auto_copy = {str(DEFAULTS['gui']['auto_copy']).lower()}",
            f"auto_clear_clipboard = {DEFAULTS['gui']['auto_clear_clipboard']}",
        ]

        with open(config_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

        # 🔐 Установить права 600 (чтение/запись только владельцу)
        try:
            os.chmod(config_path, 0o600)
            logger.info(f"Config file permissions set to 600: {config_path}")
        except Exception as e:
            logger.warning(f"Could not set config file permissions: {e}")

        logger.info(f"Default config created: {config_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create default config: {e}")
        return False
