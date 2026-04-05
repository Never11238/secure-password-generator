"""
Configuration management for passgen.
Handles loading and merging user settings from ~/.passgen.toml
"""

import sys
from pathlib import Path
from typing import Any

# Import TOML parser: built-in for 3.11+, fallback for older
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


DEFAULTS: dict[str, Any] = {
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
    """Return path to user config file: ~/.passgen.toml"""
    return Path.home() / CONFIG_FILENAME


def load_config() -> dict[str, Any]:
    """Load and merge user config from ~/.passgen.toml."""
    config = _deep_copy(DEFAULTS)
    config_path = get_config_path()

    if not config_path.exists() or tomllib is None:
        return config

    try:
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)
        _deep_merge(config, user_config)
    except (OSError, PermissionError, tomllib.TOMLDecodeError):
        pass

    return config


def _deep_copy(obj: Any) -> Any:
    """Simple deep copy for config dicts."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(item) for item in obj]
    return obj


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Recursively merge override into base (modifies base in-place)"""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def create_default_config(overwrite: bool = False) -> bool:
    """Create ~/.passgen.toml with documented defaults."""
    config_path = get_config_path()
    if config_path.exists() and not overwrite:
        return False

    content = """# ~/.passgen.toml
# Secure Password Generator - User Configuration
verbose = false
output_format = "text"
auto_copy = false
clear_clipboard_after = 0
suppress_warnings = false

[random]
length = 24
min_entropy = 80.0
exclude_ambiguous = false
require_all_types = true
charset = "full"

[passphrase]
words = 5
capitalize = true
add_number = true
add_symbol = false
separator = "-"

[hash]
algorithm = "argon2"
pbkdf2_iterations = 100000
argon2_time_cost = 3

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
