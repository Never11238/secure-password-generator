"""
Secure Password Generator Package.

NIST SP 800-63B Rev. 4 (2025) compliant password generation
with cryptographically secure random number generation (CSPRNG).

Features:
    - CSPRNG via secrets module (NOT random)
    - Entropy calculation (Shannon formula)
    - Blacklist checking (10,000+ weak passwords)
    - Diceware passphrase generation
    - PBKDF2-HMAC-SHA256 hashing with salt
    - Secure memory handling
    - Cross-platform clipboard support

NIST SP 800-63B Rev. 4 (2025) compliant password generation
with cryptographically secure random number generation (CSPRNG).

Author: Shekhovtsov
Version: 2.0.0
License: MIT

"""

__version__ = "2.0.0"
__author__ = "Shekhovtsov"
__license__ = "MIT"

from src.generator import LowEntropyError, PasswordGenerator, PasswordGeneratorError

__all__ = [
    "LowEntropyError",
    "PasswordGenerator",
    "PasswordGeneratorError",
    "__version__",
]
