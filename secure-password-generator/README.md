# 🔐 Secure Password Generator v2.0

**NIST SP 800-63B Rev. 4 (2025) compliant** password generator with CSPRNG.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/user/passgen/actions/workflows/tests.yml/badge.svg)](https://github.com/user/passgen/actions)

## New in v2.0

- ✅ **NIST compliant**: `require_all_types=False` by default
- ✅ **Entropy validation**: Minimum 80 bits with regeneration
- ✅ **Clipboard support**: Cross-platform without dependencies
- ✅ **Memory security**: Secure password wiping
- ✅ **Hidden input**: `getpass` for check/hash commands
- ✅ **Auto-update**: Download wordlists from trusted sources
- ✅ **Metadata logging**: Without password storage
- ✅ **Random length ranges**: `--length 16-24`

## Installation

```bash
# Minimal installation
pip install secure-password-generator

# With clipboard support
pip install secure-password-generator[clipboard]

# Full installation (recommended)
pip install secure-password-generator[enhanced]

# Development installation
git clone https://github.com/user/passgen.git
cd passgen
pip install -e ".[dev]"
## 🔒 Security

This project follows security best practices:

- **CSPRNG**: Uses `secrets` module (not `random`) for cryptographic randomness
- **Static Analysis**: Code is scanned on every commit with:
  - `ruff` - Linting and style checks
  - `bandit` - Security vulnerability scanning
  - `safety` - Dependency vulnerability checking
- **Compliance**: Follows NIST SP 800-63B Rev. 4 guidelines
- **Testing**: 90%+ code coverage required for CI pass

See [Threat Model](docs/THREAT_MODEL.md) for detailed security analysis.

### Security Scan Results

[![Security Check](https://github.com/yourusername/secure-password-generator/actions/workflows/security.yml/badge.svg)](https://github.com/yourusername/secure-password-generator/actions/workflows/security.yml)