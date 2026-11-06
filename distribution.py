"""Read the distribution channel embedded in each PyInstaller build.

Source runs use the existing GitHub behavior. A frozen executable with missing
or invalid metadata fails closed: it must never launch the GitHub installer.
"""
import json
import sys
from pathlib import Path


def distribution_channel():
    if not getattr(sys, "frozen", False):
        return "github"
    try:
        metadata = Path(__file__).resolve().parent / "build_metadata" / "distribution.json"
        channel = json.loads(metadata.read_text(encoding="utf-8"))["channel"]
        return channel if channel in ("github", "store") else "unknown"
    except (OSError, ValueError, KeyError, TypeError):
        return "unknown"


def github_updates_enabled():
    return distribution_channel() == "github"
