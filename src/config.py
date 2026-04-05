"""
Configuration management for passgen.
Handles loading, saving, and merging user settings from ~/.passgen.toml
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

# Import tomllib for Python 3.11+, or tomli for older versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


# Default configuration values
DEFAULTS = {
    "verbose": False,
    "output_format": "text",
    "auto_copy": False,
    "clear_clipboard_after": 0,
    "suppress_warnings": False,
    "random": {
        "length": 16,
        "min_entropy": 80.0,
        "exclude_ambiguous": False,
        "require_all_types": False,
        "charset": "full",
    },
    "passphrase": {
        "words": 4,
        "capitalize": False,
        "add_number": False,
        "add_symbol": False,
        "separator": "-",
    },
    "hash": {
        "algorithm": "pbkdf2",
        "pbkdf2_iterations": 100_000,
        "argon2_time_cost": 3,
    },
    "check": {
        "warn_below_entropy": 60.0,
        "check_pwned": False,
    },
}

CONFIG_FILENAME = ".passgen.toml"


def get_config_path() -> Path:
    """
    Get the path to the user config file.
    Returns ~/.passgen.toml on all platforms.
    """
    return Path.home() / CONFIG_FILENAME


def load_config() -> dict[str, Any]:
    """
    Load user configuration from ~/.passgen.toml.
    Returns merged config: defaults + user settings.
    If file doesn't exist or is invalid, returns defaults.
    """
    config = DEFAULTS.copy()
    config_path = get_config_path()

    if not config_path.exists():
        return config

    if tomllib is None:
        # Can't parse TOML without library
        return config

    try:
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)

        # Deep merge: user settings override defaults
        _deep_merge(config, user_config)
        return config

    except (tomllib.TOMLDecodeError, OSError, PermissionError):
        # Invalid TOML or can't read file → return defaults
        return config


def _deep_merge(base: dict, override: dict) -> None:
    """
    Recursively merge override dict into base dict.
    Modifies base in-place.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def save_config(config: dict[str, Any], path: Optional[Path] = None) -> bool:
    """
    Save configuration to ~/.passgen.toml.
    Returns True on success, False on failure.

    Note: Writing TOML requires 'tomli-w' or 'toml' package.
    For simplicity, we skip auto-save in CLI; users edit manually.
    """
    # Optional feature: auto-save on `passgen --save-config`
    # For now, we let users edit the file manually
    return False


def create_default_config(overwrite: bool = False) -> bool:
    """
    Create a new config file with default values and comments.
    Returns True if created, False if exists and overwrite=False.
    """
    config_path = get_config_path()

    if config_path.exists() and not overwrite:
        return False

    # TOML content with comments (users can edit this)
    content = """# ~/.passgen.toml
# Secure Password Generator - User Configuration
# Edit this file to set your default preferences.
# Changes take effect on next run.

# === ОБЩИЕ НАСТРОЙКИ ===
# Показывать подробный вывод (по умолчанию: false)
verbose = false

# Формат вывода: "text" или "json"
output_format = "text"

# Автоматически копировать результат в буфер обмена
auto_copy = false

# Очищать буфер через N секунд (0 = не очищать)
clear_clipboard_after = 0

# Подавлять предупреждения
suppress_warnings = false


# === НАСТРОЙКИ ГЕНЕРАЦИИ ПАРОЛЕЙ ===
[random]
length = 24
min_entropy = 80.0
exclude_ambiguous = false
require_all_types = true
charset = "full"


# === НАСТРОЙКИ ПАРОЛЬНЫХ ФРАЗ ===
[passphrase]
words = 5
capitalize = true
add_number = true
add_symbol = false
separator = "-"


# === НАСТРОЙКИ ХЕШИРОВАНИЯ ===
[hash]
algorithm = "argon2"
pbkdf2_iterations = 100000
argon2_time_cost = 3


# === НАСТРОЙКИ ПРОВЕРКИ ПАРОЛЕЙ ===
[check]
warn_below_entropy = 60.0
check_pwned = false
"""

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except (OSError, PermissionError):
        return False
