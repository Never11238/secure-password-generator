"""
Command-Line Interface for Password Generator.
"""

import argparse
import getpass
import json
import logging
import sys
from typing import Any, Optional, Tuple

from src.clipboard import Clipboard
from src.config import create_default_config, get_config_path, load_config
from src.generator import LowEntropyError, PasswordGenerator, PasswordGeneratorError
from src.updater import Updater

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=format_str, stream=sys.stderr)


def _copy_with_auto_clear(
    clipboard, password: str, clear_seconds: Optional[int], no_warnings: bool
) -> None:
    """
    Copy password to clipboard and optionally schedule auto-clear.

    Args:
        clipboard: Clipboard instance
        password: Password string to copy
        clear_seconds: Auto-clear delay in seconds (None = disabled)
        no_warnings: Suppress warning messages
    """
    if not no_warnings:
        print(
            "⚠️ Warning: Clipboard may be accessible to other apps.",
            file=sys.stderr,
        )

    clipboard.copy(password)

    if clear_seconds and clear_seconds > 0:
        import threading
        import time

        def clear_later():
            time.sleep(clear_seconds)
            clipboard.copy(" ")
            if not no_warnings:
                print(
                    f"\n✓ Clipboard cleared after {clear_seconds}s",
                    file=sys.stderr,
                )

        timer = threading.Timer(0, clear_later)
        timer.daemon = True
        timer.start()
        if not no_warnings:
            print(
                f"⏱ Clipboard will auto-clear in {clear_seconds}s",
                file=sys.stderr,
            )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="passgen",
        description="NIST SP 800-63B Rev. 4 compliant secure password generator",
        epilog="Examples:\n  passgen --random --length 20\n  passgen --passphrase --words 6",
    )

    # === MODES (mutually exclusive) ===
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--random", action="store_true", help="Generate random password")
    mode.add_argument("--passphrase", action="store_true", help="Generate passphrase")
    mode.add_argument("--check", nargs="?", const="", metavar="PASSWORD", help="Check strength")
    mode.add_argument("--hash", nargs="?", const="", metavar="PASSWORD", help="Hash password")
    mode.add_argument("--update-all", action="store_true", help="Update wordlists")

    # === GLOBAL OPTIONS ===
    parser.add_argument(
        "-l", "--length", type=str, default="16", help="Length or range (e.g. 16-24)"
    )
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of passwords")
    parser.add_argument(
        "--charset",
        choices=["lower", "upper", "digits", "symbols", "full"],
        default="full",
    )
    parser.add_argument("--no-ambiguous", action="store_true", help="Exclude l1Ii0Oo")
    parser.add_argument("--require-all-types", action="store_true", help="Force complexity rules")
    parser.add_argument("--min-entropy", type=float, default=80.0, help="Min entropy bits")

    # === HASH OPTIONS (modifier, not a mode) ===
    parser.add_argument(
        "--hash-algo",
        type=str,
        choices=["pbkdf2", "argon2"],
        default="pbkdf2",
        help="Hash algorithm (default: pbkdf2, recommended: argon2)",
    )

    # === PASSPHRASE OPTIONS ===
    parser.add_argument("--words", type=int, default=6)
    parser.add_argument("--capitalize", action="store_true")
    parser.add_argument("--add-number", action="store_true")
    parser.add_argument("--add-symbol", action="store_true")

    # === OUTPUT OPTIONS ===
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--copy", action="store_true", help="Copy last to clipboard")
    parser.add_argument(
        "--clear-clipboard",
        type=int,
        metavar="SECONDS",
        help="Auto-clear clipboard after N seconds (requires --copy)",
    )
    parser.add_argument("--no-warnings", action="store_true")

    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--force", action="store_true")

    return parser


def parse_length(val: str) -> Tuple[int, int]:
    if "-" in val:
        parts = val.split("-")
        return int(parts[0]), int(parts[1])
    return int(val), int(val)


def run_random(args, gen, clipboard):
    min_l, max_l = parse_length(args.length)
    outputs = []

    import secrets

    for _ in range(args.count):
        length = min_l
        if min_l != max_l:
            length = min_l + secrets.randbelow(max_l - min_l + 1)

        try:
            pwd, meta = gen.generate_random(
                length=length,
                charset=args.charset,
                exclude_ambiguous=args.no_ambiguous,
                require_all_types=args.require_all_types,
                check_entropy=True,
            )
            outputs.append((pwd, meta))
        except (PasswordGeneratorError, LowEntropyError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Output
    if args.json:
        data = [{"password": p, "entropy": m["entropy_bits"]} for p, m in outputs]
        print(json.dumps(data))
    else:
        for pwd, meta in outputs:
            print(pwd)
            print(f"Entropy: {meta['entropy_bits']:.1f} bits", file=sys.stderr)
            if meta.get("warnings"):
                print(f"Warnings: {meta['warnings']}", file=sys.stderr)

    # Clipboard with optional auto-clear
    if args.copy and outputs:
        _copy_with_auto_clear(clipboard, outputs[-1][0], args.clear_clipboard, args.no_warnings)

    return 0


def run_passphrase(args, gen, clipboard):
    outputs = []
    for _ in range(args.count):
        try:
            pwd, meta = gen.generate_passphrase(
                words=args.words,
                capitalize=args.capitalize,
                add_number=args.add_number,
                add_symbol=args.add_symbol,
            )
            outputs.append((pwd, meta))
        except (PasswordGeneratorError, LowEntropyError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps([{"passphrase": p, "entropy": m["entropy_bits"]} for p, m in outputs]))
    else:
        for pwd, meta in outputs:
            print(pwd)
            print(f"Entropy: {meta['entropy_bits']:.1f} bits", file=sys.stderr)

    # Clipboard with optional auto-clear
    if args.copy and outputs:
        _copy_with_auto_clear(clipboard, outputs[-1][0], args.clear_clipboard, args.no_warnings)
    return 0


def run_check(args, gen):
    pwd = args.check
    if pwd == "":
        pwd = getpass.getpass("Password: ")
    if not pwd:
        print("Error: No password", file=sys.stderr)
        return 1

    result = gen.check_strength(pwd)
    if args.json:
        print(json.dumps(result))
    else:
        print(f"Strength: {result['strength'].upper()}")
        print(f"Entropy: {result['entropy_bits']:.1f} bits")
        if result.get("recommendations"):
            for r in result["recommendations"]:
                print(f" - {r}")
    return 0


def run_hash(args, gen):
    """Hash password with specified algorithm."""
    pwd = args.hash
    if pwd == "":
        pwd = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm: ")
        if pwd != confirm:
            print("Error: Mismatch", file=sys.stderr)
            return 1

    if not pwd:
        return 1

    try:
        # Передаём algorithm из аргументов
        res = gen.hash_password(pwd, algorithm=args.hash_algo)
    except PasswordGeneratorError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res))
    else:
        print(f"\n{'=' * 60}")
        print("Password Hash")
        print(f"{'=' * 60}")
        print(f"Algorithm:     {res['algorithm'].upper()}")

        if "iterations" in res:
            print(f"Iterations:    {res['iterations']:,}")
        if "params" in res:
            print(f"Parameters:    {res['params']}")
        if "salt" in res:
            print(f"Salt:          {res['salt']}")
        print(f"Hash:          {res['hash']}")

        if res.get("algorithm") == "argon2id":
            print("\n✓ Argon2id recommended for new applications")
        else:
            print("\nStore both hash AND salt for verification")
        print(f"{'=' * 60}\n")

    return 0


def main() -> int:
    # Handle --init-config first (before any other logic)
    if "--init-config" in sys.argv:
        if create_default_config(overwrite="--force" in sys.argv):
            print(f"✅ Config created: {get_config_path()}", file=sys.stderr)
        else:
            print(f"⚠️ Config already exists: {get_config_path()}", file=sys.stderr)
            print("Use --init-config --force to overwrite", file=sys.stderr)
        return 0

    # Load user configuration
    config = load_config()

    # Apply config defaults to sys.argv (CLI args still win)
    _apply_config_to_argv(config)
    parser = create_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    gen = PasswordGenerator(min_entropy=args.min_entropy, enable_logging=args.verbose)
    clipboard = Clipboard()

    if args.random:
        return run_random(args, gen, clipboard)
    elif args.passphrase:
        return run_passphrase(args, gen, clipboard)
    elif args.check is not None:
        return run_check(args, gen)
    elif args.hash is not None:
        return run_hash(args, gen)
    elif args.update_all:
        upd = Updater()
        print("Updating lists...")
        success, msg = upd.update_all(force=args.force)
        print(f"Status: {'OK' if success else 'FAIL'} - {msg}")
        return 0 if success else 1

    return 0


def _apply_config_to_argv(config: dict[str, Any]) -> None:
    """
    Inject config defaults into sys.argv before argparse parsing.
    CLI arguments always take precedence over config values.
    """
    # Skip if no mode specified (will show help)
    modes = {"--random", "--passphrase", "--check", "--hash", "--update-all"}
    if not any(arg in modes for arg in sys.argv):
        return

    # === GLOBAL SETTINGS ===
    if config.get("auto_copy") and "--copy" not in sys.argv:
        sys.argv.append("--copy")

    if config.get("clear_clipboard_after", 0) > 0:
        if "--clear-clipboard" not in sys.argv:
            sys.argv.extend(["--clear-clipboard", str(config["clear_clipboard_after"])])

    if config.get("suppress_warnings") and "--no-warnings" not in sys.argv:
        sys.argv.append("--no-warnings")

    if config.get("verbose") and "-v" not in sys.argv and "--verbose" not in sys.argv:
        sys.argv.append("--verbose")

    # === MODE-SPECIFIC SETTINGS ===
    if "--random" in sys.argv:
        rand = config.get("random", {})
        if "--length" not in sys.argv and "-l" not in sys.argv:
            sys.argv.extend(["--length", str(rand.get("length", 16))])
        if rand.get("exclude_ambiguous") and "--no-ambiguous" not in sys.argv:
            sys.argv.append("--no-ambiguous")
        if rand.get("require_all_types") and "--require-all-types" not in sys.argv:
            sys.argv.append("--require-all-types")
        if "charset" in rand and "--charset" not in sys.argv:
            sys.argv.extend(["--charset", rand["charset"]])

    elif "--passphrase" in sys.argv:
        phrase = config.get("passphrase", {})
        if "--words" not in sys.argv:
            sys.argv.extend(["--words", str(phrase.get("words", 4))])
        if phrase.get("capitalize") and "--capitalize" not in sys.argv:
            sys.argv.append("--capitalize")
        if phrase.get("add_number") and "--add-number" not in sys.argv:
            sys.argv.append("--add-number")
        if phrase.get("add_symbol") and "--add-symbol" not in sys.argv:
            sys.argv.append("--add-symbol")
        if "separator" in phrase and "--separator" not in sys.argv:
            sys.argv.extend(["--separator", phrase["separator"]])

    elif "--hash" in sys.argv:
        hash_cfg = config.get("hash", {})
        if "--hash-algo" not in sys.argv:
            sys.argv.extend(["--hash-algo", hash_cfg.get("algorithm", "pbkdf2")])

    # Note: --check settings (warn_below_entropy, check_pwned)
    # are applied inside the check logic, not via argv


if __name__ == "__main__":
    import sys

    try:
        # Run the main CLI application
        main()
    except SystemExit:
        # argparse calls sys.exit(0) on --help or success, and sys.exit(2) on error
        if len(sys.argv) == 1:
            print("\n[TIP] Use --help to see all commands.")

        # Keep console open ONLY if running interactively (e.g., double-click on Windows)
        # Skips pause in CI/CD or when output is redirected
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                input("\n[Press Enter to close...]")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(0)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"\n[ERROR] Unhandled error: {e}")

        # Keep window open only if running interactively
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                input("\n[Press Enter to close...]")
            except (EOFError, KeyboardInterrupt):
                pass
        sys.exit(1)
