"""Tests for configuration management"""

import os
import tempfile
from pathlib import Path

from src.config import (
    load_config,
    create_default_config,
    get_config_path,
    _deep_merge,
    _deep_copy,
)


def test_deep_merge():
    """Test recursive merging of config dicts"""
    base = {"a": 1, "b": {"x": 10, "y": 20}, "c": [1, 2]}
    override = {"b": {"y": 99, "z": 30}, "c": [3], "d": 4}
    _deep_merge(base, override)
    assert base["a"] == 1
    assert base["b"] == {"x": 10, "y": 99, "z": 30}
    assert base["c"] == [3]  # lists are replaced, not merged
    assert base["d"] == 4


def test_deep_copy():
    """Test that _deep_copy doesn't share references"""
    original = {"a": [1, 2], "b": {"x": 10}}
    copied = _deep_copy(original)
    copied["a"].append(3)
    copied["b"]["x"] = 99
    assert original["a"] == [1, 2]
    assert original["b"]["x"] == 10


def test_load_config_defaults_when_missing():
    """When no config file exists, return defaults"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily override home directory
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            config = load_config()
            assert config["random"]["length"] == 16
            assert config["passphrase"]["words"] == 4
            assert get_config_path().exists() is False
        finally:
            if old_home:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)


def test_create_default_config():
    """Test creation of documented config file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            # Create config
            assert create_default_config() is True
            config_path = get_config_path()
            assert config_path.exists()

            # Check content has expected sections
            content = config_path.read_text(encoding="utf-8")
            assert "[random]" in content
            assert "length = 24" in content
            assert "# === ОБЩИЕ НАСТРОЙКИ ===" in content

            # Second call without overwrite should fail
            assert create_default_config() is False
            assert create_default_config(overwrite=True) is True
        finally:
            if old_home:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)


def test_load_config_with_user_overrides():
    """User config should override defaults"""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            # Create config with custom values
            config_path = get_config_path()
            config_path.write_text(
                "[random]\nlength = 32\nrequire_all_types = true\n", encoding="utf-8"
            )

            config = load_config()
            assert config["random"]["length"] == 32  # overridden
            assert config["random"]["require_all_types"] is True  # overridden
            assert config["random"]["min_entropy"] == 80.0  # default preserved
            assert config["passphrase"]["words"] == 4  # default preserved
        finally:
            if old_home:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)
