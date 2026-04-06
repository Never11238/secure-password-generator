"""
Secure Password Generator GUI v2.6.0
Features: Generator, Passphrase, Password Checker, Real-time Strength Meter
"""

import sys
import os
import math
import re
import logging
import urllib.request
import json

import customtkinter as ctk
from src.generator import PasswordGenerator
from src.config import load_config

# Настройка логирования
logger = logging.getLogger(__name__)

# Fix PyInstaller path resolution
if getattr(sys, "frozen", False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_PATH not in sys.path:
    sys.path.insert(0, BASE_PATH)


class PassGenApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🔐 Secure Password Generator")
        self.geometry("520x550")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.config = load_config()
        default_length = self.config.get("random", {}).get("length", 16)

        # --- TABS ---
        self.tabview = ctk.CTkTabview(self, width=500)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_gen = self.tabview.add("🔑 Генератор")
        self.tab_check = self.tabview.add("🛡️ Проверка")

        # ================= GENERATOR TAB =================
        self._setup_generator_tab(default_length)

        # ================= CHECKER TAB =================
        self._setup_checker_tab()

        # ================= GLOBAL STRENGTH BAR =================
        self.frame_strength = ctk.CTkFrame(self)
        self.frame_strength.pack(fill="x", padx=15, pady=(0, 15))

        self.label_strength = ctk.CTkLabel(
            self.frame_strength, text="Сила пароля: —", font=("Arial", 12, "bold")
        )
        self.label_strength.pack(side="left", padx=10, pady=8)

        self.progress_strength = ctk.CTkProgressBar(self.frame_strength, width=300)
        self.progress_strength.set(0)
        self.progress_strength.pack(side="right", padx=10, pady=8)

    def _setup_generator_tab(self, default_length):
        self.label_title = ctk.CTkLabel(
            self.tab_gen, text="Создай надёжный пароль", font=("Arial", 18, "bold")
        )
        self.label_title.pack(pady=(10, 15))

        self.mode_switch = ctk.CTkSegmentedButton(
            self.tab_gen, values=["🔑 Пароль", "📝 Фраза"], command=self.switch_gen_mode
        )
        self.mode_switch.pack(pady=5, padx=20, fill="x")
        self.mode_switch.set("🔑 Пароль")

        self.frame_slider = ctk.CTkFrame(self.tab_gen)
        self.frame_slider.pack(pady=10, fill="x", padx=20)
        self.label_length = ctk.CTkLabel(self.frame_slider, text="Длина: 16")
        self.label_length.pack(side="left", padx=10)
        self.slider_length = ctk.CTkSlider(
            self.frame_slider,
            from_=8,
            to=64,
            number_of_steps=56,
            command=self.update_slider_label,
        )
        self.slider_length.set(default_length)
        self.slider_length.pack(side="right", padx=10, fill="x", expand=True)
        # Пресеты длины пароля / количества слов
        self.frame_presets = ctk.CTkFrame(self.tab_gen)
        self.frame_presets.pack(pady=5, fill="x", padx=20)

        self.label_presets = ctk.CTkLabel(
            self.frame_presets, text="Быстрые пресеты:", font=("Arial", 10)
        )
        self.label_presets.pack(side="left", padx=10)

        # Контейнер для кнопок пресетов
        self.frame_preset_buttons = ctk.CTkFrame(self.frame_presets)
        self.frame_preset_buttons.pack(side="left", fill="x", expand=True)

        # Создаём пресеты для пароля (по умолчанию)
        self._create_preset_buttons([8, 12, 16, 20, 32])
        self.entry_output = ctk.CTkEntry(
            self.tab_gen,
            placeholder_text="Результат появится здесь...",
            font=("Consolas", 14),
            height=40,
            state="readonly",
        )
        self.entry_output.pack(pady=20, fill="x", padx=20)

        self.frame_buttons = ctk.CTkFrame(self.tab_gen)
        self.frame_buttons.pack(pady=5)

        # Кнопка 1: Сгенерировать
        ctk.CTkButton(
            self.frame_buttons,
            text="🔄 Сгенерировать",
            command=self.generate,
            fg_color="green",
            hover_color="#006400",
        ).pack(side="left", padx=5)

        # Кнопка 2: Копировать
        ctk.CTkButton(
            self.frame_buttons,
            text="📋 Копировать",
            command=self.copy_to_clip,
            fg_color="#1f6aa5",
            hover_color="#144870",
        ).pack(side="left", padx=5)

        # Кнопка 3: Проверить обновления
        ctk.CTkButton(
            self.frame_buttons,
            text="🔍 Обновления",
            command=self.check_for_updates,
            fg_color="#808080",
            hover_color="#505050",
        ).pack(side="left", padx=5)

    def _setup_checker_tab(self):
        self.label_title2 = ctk.CTkLabel(
            self.tab_check, text="Проверь стойкость пароля", font=("Arial", 18, "bold")
        )
        self.label_title2.pack(pady=(10, 15))

        self.check_var = ctk.StringVar()
        self.entry_check = ctk.CTkEntry(
            self.tab_check,
            textvariable=self.check_var,
            placeholder_text="Вставь или введи пароль...",
            font=("Consolas", 14),
            height=40,
        )
        self.entry_check.pack(pady=15, fill="x", padx=20)
        self.check_var.trace_add("write", self.on_check_input)

        self.label_feedback = ctk.CTkLabel(
            self.tab_check, text="", wraplength=450, justify="left"
        )
        self.label_feedback.pack(pady=10, padx=20, fill="x")

    # ================= LOGIC =================
    def switch_gen_mode(self, mode):
        if "Пароль" in mode:
            self.slider_length.configure(from_=8, to=64, number_of_steps=56)
            self.slider_length.set(16)
            self.label_length.configure(text="Длина: 16")
        else:
            self.slider_length.configure(from_=3, to=8, number_of_steps=5)
            self.slider_length.set(4)
            self.label_length.configure(text="Слов: 4")
        self._update_presets()

    def update_slider_label(self, val):
        mode = self.mode_switch.get()
        label = "Длина" if "Пароль" in mode else "Слов"
        self.label_length.configure(text=f"{label}: {int(val)}")

    def set_preset_length(self, length: int) -> None:
        """Установить длину пароля из пресета."""
        self.slider_length.set(length)
        self.update_slider_label(length)

    def _create_preset_buttons(self, presets: list) -> None:
        """Создать кнопки пресетов (с полной очисткой старых)."""
        # Полная очистка всех виджетов внутри фрейма кнопок
        for widget in self.frame_preset_buttons.winfo_children():
            widget.destroy()

        # Небольшая задержка для гарантированного обновления интерфейса (опционально)
        self.update_idletasks()

        # Создаём новые кнопки
        for preset_value in presets:
            ctk.CTkButton(
                self.frame_preset_buttons,
                text=str(preset_value),
                width=45,
                command=lambda v=preset_value: self.set_preset_length(v),
            ).pack(side="left", padx=3)

    def _update_presets(self) -> None:
        """Обновить пресеты в зависимости от режима."""
        mode = self.mode_switch.get()
        if "Пароль" in mode:
            # Пресеты для длины пароля (символы)
            self._create_preset_buttons([8, 12, 16, 20, 32])
        else:
            # Пресеты для количества слов (фразы)
            self._create_preset_buttons([3, 4, 5, 6, 8])

    def generate(self):
        try:
            length = int(self.slider_length.get())
            mode = self.mode_switch.get()

            gen = PasswordGenerator(
                min_length=length, max_length=length, enable_logging=False
            )

            if "Пароль" in mode:
                pwd, meta = gen.generate_random()
            else:
                pwd, meta = gen.generate_passphrase(words=length)

            self.entry_output.configure(state="normal")
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, pwd)
            self.entry_output.configure(state="readonly")

            self.update_strength_ui(meta.get("entropy", 0) or len(pwd) * 6.55)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            self.entry_output.configure(state="normal")
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, f"Ошибка: {e}")
            self.entry_output.configure(state="readonly")

    def copy_to_clip(self):
        pwd = self.entry_output.get()
        if pwd and not pwd.startswith("Ошибка"):
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.update()
            self.label_strength.configure(text="✅ Скопировано!", text_color="green")
            self.after(
                1500, lambda: self.label_strength.configure(text="Сила пароля: —")
            )

    def on_check_input(self, *args):
        pwd = self.check_var.get()
        if not pwd:
            self.update_strength_ui(0)
            self.label_feedback.configure(text="")
            return

        # Расчет энтропии (фоллбэк, если в ядре нет check_метода)
        charset_size = 0
        if re.search(r"[a-z]", pwd):
            charset_size += 26
        if re.search(r"[A-Z]", pwd):
            charset_size += 26
        if re.search(r"[0-9]", pwd):
            charset_size += 10
        if re.search(r"[^a-zA-Z0-9]", pwd):
            charset_size += 32

        entropy = len(pwd) * (math.log2(charset_size) if charset_size > 0 else 0)
        self.update_strength_ui(entropy)

        # Обратная связь
        if entropy < 35:
            self.label_feedback.configure(
                text="⚠️ Слабый: слишком короткий или простой шаблон",
                text_color="orange",
            )
        elif entropy < 60:
            self.label_feedback.configure(
                text="🟡 Средний: допустимо для второстепенных аккаунтов",
                text_color="orange",
            )
        else:
            self.label_feedback.configure(
                text="🟢 Надёжный: соответствует NIST SP 800-63B", text_color="green"
            )

    def update_strength_ui(self, entropy):
        entropy = max(0, min(entropy, 120))
        progress = entropy / 120.0
        self.progress_strength.set(progress)

        if entropy < 40:
            color, txt = "#ff4d4d", "Слабый 🔴"
        elif entropy < 75:
            color, txt = "#ffcc00", "Средний 🟡"
        else:
            color, txt = "#33cc33", "Надёжный 🟢"

        self.label_strength.configure(
            text=f"Сила: {txt} ({entropy:.1f} бит)", text_color=color
        )
        self.progress_strength.configure(progress_color=color)

    def check_for_updates(self):
        """Проверяет наличие новой версии на GitHub"""
        self.label_strength.configure(text="🔄 Проверка...", text_color="blue")
        self.update()

        try:
            url = "https://api.github.com/repos/Never11238/secure-password-generator/releases/latest"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "SecurePasswordGenerator/2.6.0",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            latest_tag = data.get("tag_name", "v0.0.0")
            current_version = "v2.6.0"

            if latest_tag > current_version:
                self.label_strength.configure(
                    text=f"🆕 Доступно: {latest_tag}!", text_color="green"
                )
            else:
                self.label_strength.configure(
                    text="✅ Актуальная версия", text_color="green"
                )
                self.after(
                    2000, lambda: self.label_strength.configure(text="Сила пароля: —")
                )

        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP Error {e.code}: {e.reason}")
            if e.code == 404:
                self.label_strength.configure(
                    text="⚠️ Релиз не опубликован", text_color="orange"
                )
            elif e.code == 403:
                self.label_strength.configure(
                    text="⚠️ GitHub: доступ ограничен", text_color="orange"
                )
            else:
                self.label_strength.configure(
                    text=f"⚠️ Ошибка: {e.code}", text_color="orange"
                )

        except urllib.error.URLError as e:
            logger.warning(f"URL Error: {e.reason}")
            self.label_strength.configure(text="⚠️ Нет соединения", text_color="orange")

        except json.JSONDecodeError as e:
            logger.warning(f"JSON Decode Error: {e}")
            self.label_strength.configure(text="⚠️ Ошибка ответа", text_color="orange")

        except Exception as e:
            logger.error(f"Update check failed: {type(e).__name__}: {e}")
            self.label_strength.configure(
                text="⚠️ Ошибка проверки", text_color="orange"
            )


if __name__ == "__main__":
    app = PassGenApp()
    app.mainloop()
