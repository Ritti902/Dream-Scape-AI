"""Shared filesystem helpers for generated media."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]


def _resolve_output_root() -> Path:
    configured = Path(os.getenv("OUTPUT_DIR", "outputs"))
    if configured.is_absolute():
        return configured
    return BACKEND_DIR / configured


OUTPUT_ROOT = _resolve_output_root()
IMAGES_DIR = OUTPUT_ROOT / "images"
VIDEOS_DIR = OUTPUT_ROOT / "videos"
MUSIC_DIR = OUTPUT_ROOT / "music"


def ensure_output_dirs() -> None:
    for directory in (IMAGES_DIR, VIDEOS_DIR, MUSIC_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def unique_stem(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"


def media_path(folder: str, filename: str) -> Path:
    ensure_output_dirs()
    folders = {
        "images": IMAGES_DIR,
        "videos": VIDEOS_DIR,
        "music": MUSIC_DIR,
    }
    return folders[folder] / filename
