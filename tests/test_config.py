"""Тесты для модуля конфигурации."""

import pytest
import os
from pathlib import Path
from src.config import load_config, create_default_config, DEFAULTS, get_config_path
import copy

class TestConfigDefaults:
    def test_defaults_exist(self):
        """Проверка, что DEFAULTS не пустой."""
        assert isinstance(DEFAULTS, dict)
        assert "random" in DEFAULTS
        assert "passphrase" in DEFAULTS

    def test_defaults_structure(self):
        """Проверка структуры дефолтов."""
        assert DEFAULTS["random"]["length"] == 16
        assert DEFAULTS["passphrase"]["words"] == 4

class TestConfigLoad:
    def test_load_without_file(self, tmp_path, monkeypatch):
        """Загрузка без файла конфига (только дефолты)."""
        # Подменяем домашнюю директорию на временную
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        config = load_config()
        assert config == DEFAULTS  # Должны вернуться точные дефолты

    def test_load_with_custom_file(self, tmp_path, monkeypatch):
        """Загрузка с пользовательским файлом."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        # Создаём тестовый конфиг
        config_file = tmp_path / ".passgen.toml"
        config_file.write_text('[random]\nlength = 32\n')
        
        config = load_config()
        assert config["random"]["length"] == 32  # Значение перезаписано
        assert config["random"]["min_length"] == 8  # Остальное из дефолтов

class TestConfigCreate:
    def test_create_default(self, tmp_path, monkeypatch):
        """Создание файла конфига по умолчанию."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        result = create_default_config()
        assert result is True
        
        config_file = tmp_path / ".passgen.toml"
        assert config_file.exists()
        
        # Проверка прав доступа (на Windows может не работать строго, но файл должен быть создан)
        if os.name != "nt":  # Только для Linux/Mac
            mode = os.stat(config_file).st_mode & 0o777
            assert mode == 0o600

    def test_create_no_overwrite(self, tmp_path, monkeypatch):
        """Проверка, что существующий файл не перезаписывается."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        config_file = tmp_path / ".passgen.toml"
        config_file.write_text("# existing config")
        
        result = create_default_config(overwrite=False)
        assert result is False
        
        content = config_file.read_text()
        assert content == "# existing config"