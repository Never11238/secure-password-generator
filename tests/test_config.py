"""Tests for configuration management — with proper isolation"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import after potential env changes
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
    """Test with fully isolated home directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch Path.home() to return our temp dir (works on all platforms)
        with patch("src.config.Path.home", return_value=Path(tmpdir)):
            config = load_config()
            assert config["random"]["length"] == 16  # дефолт
            assert config["passphrase"]["words"] == 4
            assert not (Path(tmpdir) / ".passgen.toml").exists()


def test_create_default_config():
    """Test config creation in isolated env"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.config.Path.home", return_value=Path(tmpdir)):
            # First call should create file
            assert create_default_config() is True
            config_path = Path(tmpdir) / ".passgen.toml"
            assert config_path.exists()

            content = config_path.read_text(encoding="utf-8")
            assert "[random]" in content
            assert "length = 24" in content

            # Second call without overwrite should fail
            assert create_default_config() is False
            # With overwrite should succeed
            assert create_default_config(overwrite=True) is True


def test_load_config_with_user_overrides():
    """User config should override defaults in isolated env"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.config.Path.home", return_value=Path(tmpdir)):
            # Create config with custom values
            config_path = Path(tmpdir) / ".passgen.toml"
            config_path.write_text(
                "[random]\nlength = 32\nrequire_all_types = true\n", encoding="utf-8"
            )

            config = load_config()
            assert config["random"]["length"] == 32  # overridden
            assert config["random"]["require_all_types"] is True
            assert config["random"]["min_entropy"] == 80.0  # default preserved
            assert config["passphrase"]["words"] == 4  # default preserved
