"""Cryptographically secure password generator module (NIST SP 800-63B compliant)."""

import hashlib
import json
import logging
import math
import re
import secrets
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

# Argon2 support (optional)
try:
    from argon2 import PasswordHasher
    from argon2.low_level import Type

    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    PasswordHasher = None  # type: ignore
    Type = None  # type: ignore

# zxcvbn support (optional)
try:
    from zxcvbn import zxcvbn

    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False

from src.wordlist import load_wordlist

# Configure logging
logger = logging.getLogger(__name__)


class PasswordGeneratorError(Exception):
    """Base exception for password generator errors."""

    pass


class WeakPasswordError(PasswordGeneratorError):
    """Raised when generated password is in blacklist."""

    pass


class LowEntropyError(PasswordGeneratorError):
    """Raised when password entropy is below minimum threshold."""

    pass


class PasswordGenerator:
    """Cryptographically secure password generator (CSPRNG via secrets module)."""

    # Character sets (NIST SP 800-63B compliant)
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGITS = "0123456789"
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    FULL_CHARSET = LOWERCASE + UPPERCASE + DIGITS + SYMBOLS
    AMBIGUOUS = "l1Ii0Oo"

    def __init__(
        self,
        min_length: int = 12,
        max_length: int = 64,
        min_entropy: float = 80.0,
        blacklist_path: Optional[str] = None,
        enable_history: bool = False,
        history_size: int = 100,
        enable_logging: bool = True,
    ) -> None:
        """Initialize password generator."""
        self.min_length = max(min_length, 8)
        self.max_length = max_length
        self.min_entropy = min_entropy
        self.enable_history = enable_history
        self.password_history: deque = deque(maxlen=history_size)
        self.enable_logging = enable_logging
        self.blacklist = self._load_blacklist(blacklist_path)

        logger.info(
            f"PasswordGenerator initialized: "
            f"min_len={self.min_length}, max_len={self.max_length}, "
            f"min_entropy={self.min_entropy} bits, "
            f"blacklist_size={len(self.blacklist)}"
        )

    def _load_blacklist(self, path: Optional[str] = None) -> Set[str]:
        """Load weak password blacklist from file or defaults."""
        blacklist: Set[str] = set()
        defaults = [
            "123456",
            "password",
            "123456789",
            "12345678",
            "12345",
            "1234567",
            "1234567890",
            "password123",
            "admin",
            "letmein",
            "welcome",
            "monkey",
            "master",
            "login",
            "abc123",
            "passw0rd",
            "shadow",
            "sunshine",
            "princess",
            "football",
            "iloveyou",
            "trustno1",
            "dragon",
            "baseball",
            "superman",
            "batman",
            "starwars",
            "qwerty",
            "qwerty123",
            "1234",
            "111111",
        ]
        blacklist.update(defaults)

        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        pwd = line.strip().lower()
                        if pwd:
                            blacklist.add(pwd)
                logger.info(f"Loaded blacklist from {path}")
            except FileNotFoundError:
                logger.warning(f"Blacklist file not found: {path}")
            except Exception as e:
                logger.error(f"Error loading blacklist: {e}")

        return blacklist

    def generate_random(
        self,
        length: int = 16,
        charset: str = "full",
        exclude_ambiguous: bool = False,
        require_all_types: bool = False,
        max_attempts: int = 5,
        check_entropy: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate cryptographically secure random password."""
        length = max(self.min_length, min(length, self.max_length))

        charsets = {
            "lower": self.LOWERCASE,
            "upper": self.UPPERCASE,
            "digits": self.DIGITS,
            "symbols": self.SYMBOLS,
            "full": self.FULL_CHARSET,
        }
        chars = charsets.get(charset, self.FULL_CHARSET)

        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in self.AMBIGUOUS)

        charset_size = len(chars)
        password: Optional[str] = None

        try:
            for attempt in range(1, max_attempts + 1):
                password = "".join(secrets.choice(chars) for _ in range(length))

                if require_all_types and charset == "full":
                    if not self._validate_complexity(password):
                        continue

                if password.lower() in self.blacklist:
                    if attempt < max_attempts:
                        continue
                    else:
                        raise WeakPasswordError(
                            f"Generated password is in common breach database "
                            f"(attempt {attempt}/{max_attempts})"
                        )

                if self.enable_history and self._check_duplicate(password):
                    continue

                entropy = length * math.log2(charset_size) if charset_size > 1 else 0

                if check_entropy and entropy < self.min_entropy:
                    if attempt < max_attempts:
                        logger.debug(
                            f"Attempt {attempt}: entropy {entropy:.2f} < {self.min_entropy}, retrying"
                        )
                        continue
                    else:
                        raise LowEntropyError(
                            f"Generated password has entropy {entropy:.2f} bits "
                            f"(target: {self.min_entropy}+). Consider increasing length."
                        )

                self._log_generation_event(
                    event_type="random",
                    length=length,
                    charset=charset,
                    entropy=entropy,
                    attempts=attempt,
                    require_all_types=require_all_types,
                )

                logger.info(
                    f"Password generated: {length} chars, {entropy:.2f} bits entropy"
                )

                return password, {
                    "entropy_bits": round(entropy, 2),
                    "charset_size": charset_size,
                    "attempts": attempt,
                    "require_all_types": require_all_types,
                    "warnings": [],
                }

            raise PasswordGeneratorError(
                f"Failed to generate valid password after {max_attempts} attempts"
            )

        finally:
            if password is not None:
                try:
                    del password
                except NameError:
                    pass

    def generate_passphrase(
        self,
        words: int = 6,
        separator: str = "-",
        wordlist: Optional[List[str]] = None,
        capitalize: bool = False,
        add_number: bool = False,
        add_symbol: bool = False,
        exclude_ambiguous_words: bool = True,
        max_attempts: int = 5,
        check_entropy: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate Diceware-style passphrase."""
        if wordlist is None:
            wordlist = load_wordlist()

        if exclude_ambiguous_words:
            wordlist = [w for w in wordlist if not any(c in w for c in self.AMBIGUOUS)]

        if not wordlist:
            raise PasswordGeneratorError("Wordlist is empty")

        entropy_per_word = math.log2(len(wordlist))

        try:
            for attempt in range(1, max_attempts + 1):
                selected_words = []
                for _ in range(words):
                    word = secrets.choice(wordlist)
                    selected_words.append(word.capitalize() if capitalize else word)

                passphrase = separator.join(selected_words)

                if add_number:
                    passphrase += str(secrets.randbelow(100))
                if add_symbol:
                    passphrase += secrets.choice(self.SYMBOLS)

                total_entropy = words * entropy_per_word
                if add_number:
                    total_entropy += math.log2(100)
                if add_symbol:
                    total_entropy += math.log2(len(self.SYMBOLS))

                if check_entropy and total_entropy < self.min_entropy:
                    if attempt < max_attempts:
                        continue
                    else:
                        logger.warning(
                            f"Passphrase entropy {total_entropy:.2f} < {self.min_entropy}"
                        )

                self._log_generation_event(
                    event_type="passphrase",
                    words=words,
                    entropy=total_entropy,
                    attempts=attempt,
                )

                return passphrase, {
                    "entropy_bits": round(total_entropy, 2),
                    "word_count": words,
                    "entropy_per_word": round(entropy_per_word, 2),
                    "attempts": attempt,
                    "warnings": [],
                }

            raise PasswordGeneratorError("Failed to generate passphrase")

        finally:
            if "passphrase" in locals():
                try:
                    del passphrase
                except NameError:
                    pass

    def hash_password(
        self,
        password: str,
        salt: Optional[bytes] = None,
        algorithm: str = "pbkdf2",
        iterations: int = 100000,
    ) -> Dict[str, str]:
        """Hash password using specified algorithm."""
        if algorithm.lower() == "pbkdf2":
            return self._hash_pbkdf2(password, salt, iterations)
        elif algorithm.lower() == "argon2":
            if not ARGON2_AVAILABLE:
                raise PasswordGeneratorError(
                    "Argon2 not available. Install with: pip install argon2-cffi"
                )
            return self._hash_argon2(password, iterations)
        else:
            raise PasswordGeneratorError(f"Unsupported algorithm: {algorithm}")

    def _hash_pbkdf2(
        self, password: str, salt: Optional[bytes], iterations: int
    ) -> Dict[str, str]:
        """PBKDF2-HMAC-SHA256 hashing."""
        if salt is None:
            salt = secrets.token_bytes(32)
        password_bytes = password.encode("utf-8")
        hash_bytes = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, iterations)
        result = {
            "hash": hash_bytes.hex(),
            "salt": salt.hex(),
            "algorithm": "pbkdf2",
            "iterations": iterations,
        }
        self.password_history.append(hash_bytes.hex())
        logger.info(f"Password hashed (PBKDF2): iterations={iterations}")
        return result

    def _hash_argon2(self, password: str, memory_cost: int = 65536) -> Dict[str, str]:
        """Argon2id hashing."""
        if not ARGON2_AVAILABLE:
            raise PasswordGeneratorError("Argon2 not available")
        ph = PasswordHasher(
            time_cost=3,
            memory_cost=memory_cost,
            parallelism=4,
            hash_len=32,
            type=Type.ID,
        )
        hash_string = ph.hash(password)
        result = {
            "hash": hash_string,
            "algorithm": "argon2id",
            "params": f"time=3,memory={memory_cost},parallelism=4",
        }
        self.password_history.append(hashlib.sha256(hash_string.encode()).hexdigest())
        logger.info(f"Password hashed (Argon2id): memory_cost={memory_cost}")
        return result

    def check_strength(self, password: str) -> Dict[str, Any]:
        """Analyze password strength."""
        result = {
            "length": len(password),
            "entropy_bits": 0.0,
            "in_blacklist": False,
            "strength": "unknown",
            "recommendations": [],
        }

        unique_chars = len(set(password))
        result["entropy_bits"] = self.calculate_entropy(password, unique_chars)
        result["in_blacklist"] = password.lower() in self.blacklist

        if result["in_blacklist"]:
            result["recommendations"].append("Password is in common breach database")
            result["strength"] = "very_weak"
            return result

        if len(password) < 8:
            result["strength"] = "weak"
            result["recommendations"].append("Length < 8 characters")
        elif result["entropy_bits"] < self.min_entropy:
            result["strength"] = "moderate"
            result["recommendations"].append(f"Entropy < {self.min_entropy} bits")
        else:
            result["strength"] = "strong"

        if ZXCVBN_AVAILABLE:
            try:
                res = zxcvbn(password)
                result["zxcvbn_score"] = res["score"]
                result["zxcvbn_crack_time"] = res["crack_times_display"][
                    "offline_slow_hashing_1e4_per_second"
                ]
            except Exception as e:
                logger.debug(f"zxcvbn check failed: {e}")

        return result

    def calculate_entropy(self, password: str, charset_size: int) -> float:
        """Calculate Shannon entropy: H = L * log2(N)"""
        if charset_size <= 1:
            return 0.0
        return len(password) * math.log2(charset_size)

    def _validate_complexity(self, password: str) -> bool:
        """Check if password has at least one of each char type."""
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_symbol = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password))
        return all([has_lower, has_upper, has_digit, has_symbol])

    def _check_duplicate(self, password: str) -> bool:
        """Check if password hash is in history."""
        h = hashlib.sha256(password.encode()).hexdigest()
        return h in self.password_history

    def _log_generation_event(self, **kwargs: Any) -> None:
        """Log metadata without password."""
        if not self.enable_logging:
            return
        safe_kwargs = {
            k: v for k, v in kwargs.items() if k not in ("password", "pwd", "secret")
        }
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "password_generated",
            **safe_kwargs,
        }
        logger.debug(f"Generation event: {json.dumps(log_entry)}")
