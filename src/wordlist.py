"""Модуль загрузки словаря Diceware для генерации пассфраз."""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

WORDLIST_PATH = Path(__file__).parent.parent / "data" / "eff_wordlist.txt"

_FALLBACK_WORDS = [
    "correct",
    "horse",
    "battery",
    "staple",
    "meadow",
    "phoenix",
    "dragon",
    "shadow",
    "crystal",
    "thunder",
    "forest",
    "river",
    "mountain",
    "ocean",
    "starlight",
]


def load_wordlist() -> List[str]:
    """Загрузить список слов EFF Diceware."""
    if WORDLIST_PATH.exists():
        try:
            with open(WORDLIST_PATH, "r", encoding="utf-8") as f:
                words = []
                for line in f:
                    line = line.strip()
                    if "\t" in line:
                        word = line.split("\t", 1)[1].strip().lower()
                    else:
                        word = line.lower()
                    if word and word.isalpha() and len(word) >= 3:
                        words.append(word)
                if len(words) >= 100:
                    logger.info(f"Загружено {len(words)} слов из {WORDLIST_PATH}")
                    return words
        except Exception as e:
            logger.warning(f"Ошибка загрузки wordlist: {e}")
    logger.warning(f"Используется fallback wordlist ({len(_FALLBACK_WORDS)} слов)")
    return _FALLBACK_WORDS.copy()


__all__ = ["DICWARE_WORDLIST", "load_wordlist"]
DICWARE_WORDLIST = load_wordlist()
