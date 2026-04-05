# 🔐 Secure Password Generator v2.6.0

**Генератор паролей и пассфраз**, соответствующий стандарту **NIST SP 800-63B Rev. 4 (2025)**. Использует криптографически стойкий генератор случайных чисел (CSPRNG) для максимальной безопасности.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/github/v/release/Never11238/secure-password-generator)](https://github.com/Never11238/secure-password-generator/releases)
[![Security Check](https://github.com/Never11238/secure-password-generator/actions/workflows/security.yml/badge.svg)](https://github.com/Never11238/secure-password-generator/actions/workflows/security.yml)
[![WinGet Status](https://img.shields.io/badge/winget-pending-yellow)](https://github.com/microsoft/winget-pkgs/pull/355579)

---

## 📋 Содержание

- [Возможности](#-возможности)
- [Что нового в v2.6](#-что-нового-в-v26)
- [Установка](#-установка)
- [Быстрый старт](#-быстрый-старт)
- [Графический интерфейс (GUI)](#графический-интерфейс-gui)
- [Использование CLI](#использование-cli)
- [Конфигурация](#конфигурация)
- [Безопасность](##-безопасность)
- [Устранение неполадок](#устранение-неполадок)
- [FAQ](#faq)
- [API для разработчиков](#api-для-разработчиков)
- [Тестирование и разработка](#тестирование-и-разработка)
- [Структура проекта](#структура-проекта)
- [Вклад в проект](#вклад-в-проект)
- [Контакты и безопасность](#контакты-и-безопасность)

---

## ✨ Возможности

### Генерация паролей

- **Случайные пароли** с настраиваемой длиной (включая диапазоны, например, 16-24)
- **Пассфразы Diceware** из случайных слов (EFF wordlist)
- **Настройка сложности**: исключение неоднозначных символов, требование всех типов символов
- **Проверка энтропии**: минимальная энтропия 80 бит по умолчанию

### Безопасность

- **CSPRNG**: Используется модуль `secrets` (НЕ `random`) для криптографической случайности
- **Чёрный список**: Проверка на слабые пароли (10k наиболее распространённых)
- **Хеширование**: Поддержка PBKDF2-HMAC-SHA256 и Argon2id
- **Безопасная память**: Очистка паролей после использования (best effort)
- **История**: Опциональное хранение хешей сгенерированных паролей (без самих паролей)

### Удобство

- **Буфер обмена**: Копирование с авто-очисткой через N секунд
- **Скрытый ввод**: Команды `check` и `hash` запрашивают пароль без отображения
- **JSON вывод**: Машиночитаемый формат для интеграции
- **Автообновление**: Загрузка актуальных списков слов и чёрных списков

---

## 🆕 Что нового в v2.6

| Функция | Описание |
| ------- | -------- |
| ✅ **NIST compliant** | `require_all_types=False` по умолчанию (согласно NIST) |
| ✅ **Валидация энтропии** | Минимум 80 бит с автоматической повторной генерацией |
| ✅ **Поддержка буфера обмена** | Кроссплатформенно без внешних зависимостей |
| ✅ **Безопасность памяти** | Secure wiping паролей после использования |
| ✅ **Скрытый ввод** | `getpass` для команд check/hash |
| ✅ **Автообновление** | Загрузка wordlist из доверенных источников (EFF, SecLists) |
| ✅ **Логирование метаданных** | Без хранения самих паролей |
| ✅ **Диапазоны длины** | `--length 16-24` для случайной длины в диапазоне |
| ✅ **Графический интерфейс** | Современный GUI на CustomTkinter с вкладками и индикатором силы |
| ✅ **Авто-проверка обновлений** | Кнопка в интерфейсе проверяет новые версии на GitHub |

---

## 📦 Установка

### Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Варианты установки

```bash
# Минимальная установка (только генератор)
pip install secure-password-generator

# С поддержкой буфера обмена (pyperclip)
pip install secure-password-generator[enhanced]

# Для разработки (с тестами и линтерами)
git clone https://github.com/Never11238/secure-password-generator.git
cd secure-password-generator
pip install -e ".[dev]"
```

## Зависимости

| Пакет | Назначение | Обязательно |
| ----- | ---------- | ----------- |
| `tomli` | Парсинг TOML-конфига (для Python <3.11) | Автоматически |
| `pyperclip` | Буфер обмена | Опционально |
| `zxcvbn` | Продвинутая проверка сложности | Опционально |
| `argon2-cffi` | Хеширование Argon2id | Опционально |
| `customtkinter` | Графический интерфейс | Только для GUI |

---

## 🚀 Быстрый старт

```bash
# Сгенерировать случайный пароль (16 символов)
passgen --random

# Сгенерировать пароль длиной 24 символа
passgen --random --length 24

# Сгенерировать 5 паролей длиной 20-30 символов
passgen --random --length 20-30 --count 5

# Сгенерировать пассфразу из 6 слов
passgen --passphrase --words 6

# Проверить сложность пароля (скрытый ввод)
passgen --check

# Создать хеш пароля (PBKDF2)
passgen --hash

# Обновить словари и чёрные списки
passgen --update-all
```

---

## Графический интерфейс (GUI)

Для пользователей, предпочитающих визуальный интерфейс, доступна версия с современным GUI на CustomTkinter.

### Установка GUI-версии

```powershell
# Через WinGet (после одобрения манифеста)
winget install Never11238.passgen

# Или вручную:
# 1. Перейди в Releases: https://github.com/Never11238/secure-password-generator/releases
# 2. Скачай passgen-gui-v2.6.0.zip
# 3. Распакуй в любую папку
# 4. Запусти passgen-gui.exe
```

> ⚠️ **Windows SmartScreen**: При первом запуске может появиться предупреждение "Неизвестный издатель". Нажмите `Подробнее` → `Выполнить в любом случае`. Файл отправлен на проверку в Microsoft (PR #355579).

### Возможности GUI

- 🎨 Современный интерфейс с тёмной/светлой/системной темой
- 🔑 Генерация паролей и пассфраз в один клик
- 🛡️ Вкладка проверки стойкости с индикатором энтропии в реальном времени
- 📋 Копирование в буфер с авто-очисткой
- 🔄 Проверка обновлений прямо из приложения (кнопка "🔍 Обновления")
- ⚙️ Настройки через ~/.passgen.toml

---

## Использование CLI

### Основные команды

| Команда | Описание |
| ------- | -------- |
| `--random` | Генерация случайного пароля |
| `--passphrase` | Генерация пассфразы (Diceware) |
| `--check [PASSWORD]` | Проверка сложности пароля |
| `--hash [PASSWORD]` | Создание хеша пароля |
| `--update-all` | Обновление словарей |

### Параметры генерации случайных паролей

```bash
passgen --random [ОПЦИИ]
-l, --length VAL        Длина или диапазон (например, 16 или 16-24)
                        По умолчанию: 16
-c, --count N           Количество паролей
                        По умолчанию: 1
--charset TYPE          Набор символов: lower, upper, digits, symbols, full
                        По умолчанию: full
--no-ambiguous          Исключить неоднозначные символы (l1Ii0Oo)
--require-all-types     Требовать все типы символов (a-z, A-Z, 0-9, спецсимволы)
--min-entropy BITS      Минимальная энтропия в битах
                        По умолчанию: 80.0
```

### Параметры генерации пассфраз

```bash
passgen --passphrase [ОПЦИИ]
--words N               Количество слов
                        По умолчанию: 6
--capitalize            Капитализировать каждое слово
--add-number            Добавить случайное число в конец
--add-symbol            Добавить специальный символ в конец
```

### Параметры вывода

```bash
--json                  Вывод в формате JSON
--copy                  Копировать последний пароль в буфер обмена
--clear-clipboard SEC   Авто-очистка буфера через N секунд (только с --copy)
--no-warnings           Подавить предупреждения
-v, --verbose           Подробный режим (debug-логи)
--force                 Принудительное выполнение (для --update-all, --init-config)
```

### Примеры использования

```bash
# === СЛУЧАЙНЫЕ ПАРОЛИ ===
# Простой пароль по умолчанию
$ passgen --random
J7#mKp2$nQx9Lw4R
Entropy: 95.2 bits

# Длинный пароль без неоднозначных символов
$ passgen --random --length 32 --no-ambiguous
zT8vN3qW7rY5mK2pL9jH4xC6bF0dS1aG
Entropy: 190.4 bits

# Несколько паролей с диапазоном длины
$ passgen --random --length 16-24 --count 3
mK9$pL2nQ7xR4wJ6
Entropy: 95.2 bits
vN3zT8qW5rY7mK2pL9jH
Entropy: 126.9 bits
xC6bF0dS1aG4hU8nP5tM
Entropy: 126.9 bits

# JSON вывод для скриптов
$ passgen --random --length 20 --json
[{"password": "Kp2$nQx9Lw4RJ7#mZy5v", "entropy": 119.0}]

# === ПАССФРАЗЫ ===
# Стандартная пассфраза из 6 слов
$ passgen --passphrase
correct-horse-battery-staple-meadow-phoenix
Entropy: 77.4 bits

# Пассфраза с капитализацией и числом
$ passgen --passphrase --words 5 --capitalize --add-number
Correct-Horse-Battery-Staple-Meadow42
Entropy: 71.2 bits

# === ПРОВЕРКА СЛОЖНОСТИ ===
# Интерактивная проверка (скрытый ввод)
$ passgen --check
Password: ********
Strength: STRONG
Entropy: 95.2 bits

# Проверка конкретного пароля
$ passgen --check "mypassword123"
Strength: WEAK
Entropy: 45.3 bits
 - Password is in common breach database

# === ХЕШИРОВАНИЕ ===
# Создать хеш (интерактивно)
$ passgen --hash
Password: ********
Confirm: ********
============================================================
Password Hash
============================================================
Algorithm:     PBKDF2
Iterations:    100,000
Salt:          a3f5c8d9e2b1f4a7...
Hash:          8f3a2c1d5e9b7f4a...
Store both hash AND salt for verification
============================================================

# Хеш с Argon2id (рекомендуется)
$ passgen --hash --hash-algo argon2

# === БУФЕР ОБМЕНА ===
# Копировать с авто-очисткой через 30 секунд
$ passgen --random --length 20 --copy --clear-clipboard 30
⚠️ Warning: Clipboard may be accessible to other apps.
⏱ Clipboard will auto-clear in 30s
```

---

## Конфигурация

### Создание конфигурационного файла

```bash
# Создать файл ~/.passgen.toml с настройками по умолчанию
passgen --init-config

# Пересоздать с принудительной перезаписью
passgen --init-config --force
```

### Расположение файла конфигурации

| ОС | Путь |
| -- | ---- |
| Windows | `C:\Users\<User>\.passgen.toml` |
| Linux/macOS | `~/.passgen.toml` |

### Пример конфигурации (~/.passgen.toml)

```toml
# ~/.passgen.toml
# Secure Password Generator - Пользовательская конфигурация

# === ГЛОБАЛЬНЫЕ НАСТРОЙКИ ===
verbose = false              # Подробный режим (debug-логи)
output_format = "text"       # Формат вывода: text или json
auto_copy = false            # Авто-копирование в буфер обмена
clear_clipboard_after = 0    # Авто-очистка буфера через N секунд (0 = отключено)
suppress_warnings = false    # Подавить предупреждения

# === НАСТРОЙКИ СЛУЧАЙНЫХ ПАРОЛЕЙ ===
[random]
length = 24                  # Длина по умолчанию
min_entropy = 80.0           # Минимальная энтропия (биты)
exclude_ambiguous = false    # Исключить l1Ii0Oo
require_all_types = true     # Требовать все типы символов
charset = "full"             # Набор символов: full/lower/upper/digits/symbols

# === НАСТРОЙКИ ПАССФРАЗ ===
[passphrase]
words = 5                    # Количество слов по умолчанию
capitalize = true            # Капитализировать слова
add_number = true            # Добавлять число
add_symbol = false           # Добавлять спецсимвол
separator = "-"              # Разделитель слов

# === НАСТРОЙКИ ХЕШИРОВАНИЯ ===
[hash]
algorithm = "argon2"         # Алгоритм: pbkdf2 или argon2
pbkdf2_iterations = 100000   # Итерации для PBKDF2
argon2_time_cost = 3         # Время для Argon2

# === НАСТРОЙКИ ПРОВЕРКИ ===
[check]
warn_below_entropy = 60.0    # Предупреждать при энтропии ниже N бит
check_pwned = false          # Проверка в базе утёкших паролей (экспериментально)
```

### Приоритет настроек

1. **Аргументы командной строки** (наивысший приоритет)
2. **Файл конфигурации** `~/.passgen.toml`
3. **Встроенные значения по умолчанию** (низший приоритет)

---

### Безопасность

### Соответствие стандартам

Этот проект следует лучшим практикам безопасности:

| Стандарт | Описание |
| -------- | -------- |
| **NIST SP 800-63B Rev. 4** | Рекомендации по аутентификации (2025) |
| **ISO 27002:2021** | Контроль информационной безопасности |

### Технические меры защиты

- **CSPRNG**: Модуль `secrets` вместо `random` для криптографической случайности
- **Минимальная энтропия**: 80 бит по умолчанию (формула Шеннона: `H = L × log₂(N)`)
- **Чёрный список**: Проверка против 10,000+ распространённых паролей
- **PBKDF2-HMAC-SHA256**: 100,000 итераций по умолчанию
- **Argon2id**: Современный алгоритм хеширования (опционально)
- **Без логов паролей**: Логирование только метаданных (длина, энтропия, timestamp)

### Статический анализ кода

На каждый коммит запускаются:

```yaml
- ruff     # Линтинг и проверка стиля
- bandit   # Поиск уязвимостей безопасности
- safety   # Проверка уязвимостей зависимостей
```

### Результаты сканирования безопасности

[![Security Check](https://github.com/Never11238/secure-password-generator/actions/workflows/security.yml/badge.svg)](https://github.com/Never11238/secure-password-generator/actions/workflows/security.yml)

### Модель угроз

Подробный анализ угроз см. в документе `docs/THREAT_MODEL.md`.

### Рекомендации по использованию

1. **Используйте пассфразы** для важных аккаунтов (6+ слов)
2. **Включите авто-очистку буфера** (`--clear-clipboard 30`)
3. **Не храните пароли** в логах или истории терминала
4. **Используйте Argon2id** для хеширования новых паролей
5. **Регулярно обновляйте** чёрные списки: `passgen --update-all`

---

## Устранение неполадок

| Проблема | Решение |
| -------- | ------- |
| ❌ `ModuleNotFoundError: customtkinter` | Установи зависимости: `pip install -e ".[enhanced]"` |
| ❌ Буфер обмена не копирует (Linux) | Установи `xclip` или `xsel`: `sudo apt install xclip` |
| ❌ Windows SmartScreen блокирует запуск | Нажми `Подробнее` → `Выполнить в любом случае`. Файл отправлен на проверку в Microsoft. |
| ❌ Ошибка энтропии при генерации | Увеличь длину пароля или расширь набор символов (`--charset full`) |
| ❌ Конфиг не применяется | Проверь путь: `~/.passgen.toml` (Linux/macOS) или `%USERPROFILE%\.passgen.toml` (Windows) |
| ❌ GUI не запускается | Убедись, что папка `_internal` лежит рядом с `passgen-gui.exe` |
| ❌ Ошибка "Failed to start embedded python interpreter" | Запускай `.exe` из папки сборки, не копируй отдельно |
| ❌ Кнопка "Обновления" показывает ошибку | Проверь интернет-соединение и доступ к GitHub API |

---

## FAQ

**В: Почему по умолчанию `require_all_types=False`?**  
О: Согласно NIST SP 800-63B, принудительное требование всех типов символов снижает энтропию и ухудшает запоминаемость. Лучше использовать длинные пароли/пассфразы.

**В: Хранятся ли сгенерированные пароли?**  
О: Нет. Приложение работает полностью оффлайн, не отправляет данные и не сохраняет пароли. Только метаданные (длина, энтропия) могут логироваться при включённом `--verbose`.

**В: Можно ли использовать в коммерческих проектах?**  
О: Да, лицензия MIT разрешает любое использование, включая коммерческое, при условии сохранения уведомления об авторских правах.

**В: Как сообщить об уязвимости?**  
О: Напиши на `nlsehovcov@gmail.com` с темой `[SECURITY]` или создай приватный [Security Advisory](https://github.com/Never11238/secure-password-generator/security/advisories/new) на GitHub.

**В: Почему файл блокируется антивирусом?**  
О: Это стандартное поведение для неподписанных приложений, собранных через PyInstaller. Файл отправлен на проверку в Microsoft Defender. После одобрения блокировка снимется автоматически.

**В: Как обновить приложение?**  
О: В GUI нажмите кнопку "🔍 Обновления". В CLI используйте `passgen --update-all` для обновления словарей. Для обновления самого приложения скачайте новую версию из [Releases](https://github.com/Never11238/secure-password-generator/releases).

---

## API для разработчиков

### Базовое использование

```python
from src.generator import PasswordGenerator

# Инициализация генератора
gen = PasswordGenerator(
    min_length=12,
    max_length=64,
    min_entropy=80.0,
    enable_history=False,
    enable_logging=True,
)

# Генерация случайного пароля
password, metadata = gen.generate_random(
    length=16,
    charset="full",           # full/lower/upper/digits/symbols
    exclude_ambiguous=False,
    require_all_types=False,
    check_entropy=True,
)
print(f"Password: {password}")
print(f"Entropy: {metadata['entropy_bits']} bits")
print(f"Charset size: {metadata['charset_size']}")
print(f"Attempts: {metadata['attempts']}")

# Генерация пассфразы
passphrase, meta = gen.generate_passphrase(
    words=6,
    separator="-",
    capitalize=False,
    add_number=False,
    add_symbol=False,
)
print(f"Passphrase: {passphrase}")
print(f"Entropy: {meta['entropy_bits']} bits")
```

### Проверка сложности пароля

```python
result = gen.check_strength("MyP@ssw0rd123")
print(f"Strength: {result['strength']}")
print(f"Entropy: {result['entropy_bits']:.2f} bits")
print(f"In blacklist: {result['in_blacklist']}")
print(f"Recommendations: {result['recommendations']}")

# Если установлен zxcvbn
if 'zxcvbn_score' in result:
    print(f"Zxcvbn score: {result['zxcvbn_score']}/4")
    print(f"Crack time: {result['zxcvbn_crack_time']}")
```

### Хеширование паролей

```python
# PBKDF2-HMAC-SHA256
hash_result = gen.hash_password(
    password="MySecretPassword",
    algorithm="pbkdf2",
    iterations=100000,
)
print(f"Algorithm: {hash_result['algorithm']}")
print(f"Iterations: {hash_result['iterations']}")
print(f"Salt: {hash_result['salt']}")
print(f"Hash: {hash_result['hash']}")

# Argon2id (требуется argon2-cffi)
try:
    hash_result = gen.hash_password(
        password="MySecretPassword",
        algorithm="argon2",
        iterations=3,  # time_cost
    )
    print(f"Algorithm: {hash_result['algorithm']}")
    print(f"Parameters: {hash_result['params']}")
    print(f"Hash: {hash_result['hash']}")
except PasswordGeneratorError as e:
    print(f"Argon2 not available: {e}")
```

### Расширенные возможности

```python
# Генератор с историей и кастомным чёрным списком
gen = PasswordGenerator(
    min_entropy=90.0,
    blacklist_path="data/weak_passwords.txt",
    enable_history=True,
    history_size=100,  # хранить последние 100 хешей
)

# Расчёт энтропии
entropy = gen.calculate_entropy(password="abc123", charset_size=62)
print(f"Entropy: {entropy:.2f} bits")

# Проверка на дубликат в истории
is_duplicate = gen._check_duplicate("some_password")
```

### Обработка ошибок

```python
from src.generator import (
    PasswordGeneratorError,
    WeakPasswordError,
    LowEntropyError,
)

try:
    pwd, meta = gen.generate_random(length=8, check_entropy=True)
except LowEntropyError as e:
    print(f"Низкая энтропия: {e}")
except WeakPasswordError as e:
    print(f"Слабый пароль: {e}")
except PasswordGeneratorError as e:
    print(f"Ошибка генератора: {e}")
```

---

## Тестирование и разработка

### Запуск тестов

```bash
# Запустить все тесты с покрытием
pytest

# Запустить с подробным выводом
pytest -v

# Запустить конкретный тест
pytest tests/test_generator.py -v

# Проверка покрытия кода
pytest --cov=src --cov-report=html
```

### Требования к покрытию

CI требует минимум **15%** покрытия кода (настраивается в `pyproject.toml`).

### Линтинг и статический анализ

```bash
# Ruff (линтинг + стиль)
ruff check src/

# Bandit (безопасность)
bandit -r src/

# Safety (уязвимости зависимостей)
safety check
```

### Структура тестов

```text
tests/
├── __init__.py
├── test_config.py      # Тесты конфигурации
└── test_generator.py   # Тесты генератора
```

---

## Структура проекта

```text
/workspace/
├── README.md                 # Эта документация
├── pyproject.toml            # Конфигурация проекта и зависимости
├── requirements.txt          # Зависимости для установки
├── data/
│   ├── eff_wordlist.txt      # Словарь EFF Diceware (~7770 слов)
│   └── weak_passwords.txt    # Чёрный список слабых паролей
├── src/
│   ├── __init__.py           # Инициализация пакета
│   ├── cli.py                # Command-Line Interface
│   ├── clipboard.py          # Кроссплатформенный буфер обмена
│   ├── config.py             # Управление конфигурацией (~/.passgen.toml)
│   ├── generator.py          # Ядро генератора паролей
│   ├── gui_app.py            # Графический интерфейс (CustomTkinter)
│   ├── updater.py            # Обновление словарей из сети
│   └── wordlist.py           # Загрузка и обработка wordlist
└── tests/
    ├── __init__.py
    ├── test_config.py        # Тесты конфигурации
    └── test_generator.py     # Тесты генератора
```

### Описание модулей

| Модуль | Назначение |
| ------ | ---------- |
| `generator.py` | Основное ядро: генерация, хеширование, проверка сложности |
| `cli.py` | Интерфейс командной строки, парсинг аргументов |
| `gui_app.py` | Графический интерфейс на CustomTkinter |
| `config.py` | Загрузка и слияние конфигурации из TOML |
| `clipboard.py` | Абстракция буфера обмена (pbcopy/clip/xclip/pyperclip) |
| `updater.py` | Загрузка актуальных словарей с eff.org и GitHub |
| `wordlist.py` | Утилиты загрузки и фильтрации wordlist |

---

## Вклад в проект

### Отчёт об ошибках

Пожалуйста, создавайте issue на GitHub с:

- Описанием проблемы
- Шагами для воспроизведения
- Ожидаемым и фактическим поведением
- Версией Python и ОС

### Pull Requests

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Требования к коду

- Следуйте PEP 8
- Добавьте тесты для новых функций
- Убедитесь, что все тесты проходят
- Пройдите проверку линтеров (ruff, bandit)

---

## Контакты и безопасность

- **Автор**: Shekhovtsov ([@Never11238](https://github.com/Never11238))
- **Баги и фичи**: [GitHub Issues](https://github.com/Never11238/secure-password-generator/issues)
- **Уязвимости**: `nlsehovcov@gmail.com` (тема: `[SECURITY]`) или [GitHub Security Advisory](https://github.com/Never11238/secure-password-generator/security/advisories/new)
- **WinGet PR**: [#355579](https://github.com/microsoft/winget-pkgs/pull/355579)

---

## Лицензия

Этот проект распространяется под лицензией **MIT** — см. файл `LICENSE` для деталей.

---

## Благодарности

- **EFF** за отличный словарь Diceware
- **Daniel Miessler** за SecLists и чёрный список паролей
- **NIST** за рекомендации SP 800-63B
- Сообществу Python за превосходные библиотеки

---

> **Secure Password Generator v2.6.0** | Соответствует NIST SP 800-63B Rev. 4 (2025)
>
> [🔗 GitHub](https://github.com/Never11238/secure-password-generator) · [📦 Releases](https://github.com/Never11238/secure-password-generator/releases) · [🐛 Issues](https://github.com/Never11238/secure-password-generator/issues)
