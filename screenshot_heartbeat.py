"""Write a heartbeat each time the screenshot capture loop completes a check."""
from pathlib import Path
import os

HEARTBEAT = Path.home() / ".local" / "state" / "montaris" / "screenshot.heartbeat"


def beat():
    """Call this within screenlog.py's main capture loop (even if nothing changes)."""
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.touch()
