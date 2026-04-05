"""Tests for configuration management"""

import os
import tempfile

from src.config import (
    _deep_copy,
    _deep_merge,
    create_default_config,
    get_config_path,
    load_config,
)


def test_deep_merge():
    base = {"a": 1, "b": {"x": 10, "y": 20}, "c": [1, 2]}
    override = {"b": {"y": 99, "z": 30}, "c": [3], "d": 4}
    _deep_merge(base, override)
    assert base["a"] == 1
    assert base["b"] == {"x": 10, "y": 99, "z": 30}
    assert base["c"] == [3]
    assert base["d"] == 4


def test_deep_copy():
    original = {"a": [1, 2], "b": {"x": 10}}
    copied = _deep_copy(original)
    copied["a"].append(3)
    copied["b"]["x"] = 99
    assert original["a"] == [1, 2]
    assert original["b"]["x"] == 10


def test_load_config_defaults_when_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
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
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            assert create_default_config() is True
            config_path = get_config_path()
            assert config_path.exists()
            content = config_path.read_text(encoding="utf-8")
            assert "[random]" in content
            assert "length = 24" in content
            assert create_default_config() is False
            assert create_default_config(overwrite=True) is True
        finally:
            if old_home:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)


def test_load_config_with_user_overrides():
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            config_path = get_config_path()
            config_path.write_text(
                "[random]\nlength = 32\nrequire_all_types = true\n", encoding="utf-8"
            )
            config = load_config()
            assert config["random"]["length"] == 32
            assert config["random"]["require_all_types"] is True
            assert config["random"]["min_entropy"] == 80.0
            assert config["passphrase"]["words"] == 4
        finally:
            if old_home:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)
