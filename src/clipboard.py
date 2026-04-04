"""Cross-platform clipboard support."""

import logging
import shutil
import subprocess
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class Clipboard:
    """Handles copying text to system clipboard."""

    def __init__(self):
        self.tool = self._detect_tool()

    def _detect_tool(self) -> Optional[str]:
        if shutil.which("pbcopy"):
            return "pbcopy"
        if shutil.which("clip"):
            return "clip"
        if shutil.which("wl-copy"):
            return "wl-copy"
        if shutil.which("xclip"):
            return "xclip"
        try:
            # Check if pyperclip is available via importlib
            import importlib.util

            if importlib.util.find_spec("pyperclip") is not None:
                return "pyperclip"
        except Exception as e:
            logger.debug(f"pyperclip check failed: {e}")
        return None

    def copy(self, text: str) -> Tuple[bool, str]:
        if not self.tool:
            return (
                False,
                "No clipboard tool found. Install xclip, wl-copy, or pyperclip.",
            )

        try:
            if self.tool == "pbcopy":
                subprocess.run(
                    ["pbcopy"], input=text.encode("utf-8"), check=True  
                )
            elif self.tool == "clip":
                subprocess.run(
                    ["clip"], input=text.encode("utf-8"), check=True  
                )
            elif self.tool in ("wl-copy", "xclip"):
                cmd = [self.tool]
                if self.tool == "xclip":
                    cmd += ["-selection", "clipboard"]
                subprocess.run(cmd, input=text.encode("utf-8"), check=True)
            elif self.tool == "pyperclip":
                import pyperclip

                pyperclip.copy(text)

            return True, "Copied to clipboard."
        except Exception as e:
            logger.error(f"Clipboard error: {e}")
            return False, f"Copy failed: {e}"
