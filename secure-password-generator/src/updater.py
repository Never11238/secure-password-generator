"""Update wordlists from trusted sources."""

import logging
import urllib.error
import urllib.request
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class Updater:
    DICEWARE_URL = "https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt"
    BLACKLIST_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt"

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def update_all(self, force: bool = False) -> Tuple[bool, str]:
        msgs = []
        ok = True

        # Wordlist
        path = self.data_dir / "eff_wordlist.txt"
        if not path.exists() or force:
            try:
                with urllib.request.urlopen(self.DICEWARE_URL) as resp:  # noqa: S310
                    content = resp.read().decode("utf-8")
                    # Parse EFF format (number\tword)
                    words = [
                        line.split("\t")[1].strip() for line in content.split("\n") if "\t" in line
                    ]
                    path.write_text("\n".join(words))
                    msgs.append(f"Wordlist updated: {len(words)} words")
            except Exception as e:
                msgs.append(f"Wordlist failed: {e}")
                ok = False
        else:
            msgs.append("Wordlist up to date")

        # Blacklist
        path = self.data_dir / "weak_passwords.txt"
        if not path.exists() or force:
            try:
                with urllib.request.urlopen(self.BLACKLIST_URL) as resp:  # noqa: S310
                    content = resp.read().decode("utf-8")
                    path.write_text(content)
                    count = len([line for line in content.split("\n") if line.strip()])
                    msgs.append(f"Blacklist updated: {count} entries")
            except Exception as e:
                msgs.append(f"Blacklist failed: {e}")
                ok = False
        else:
            msgs.append("Blacklist up to date")

        return ok, "; ".join(msgs)
