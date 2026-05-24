"""Music selection/download helpers for the dream pipeline."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import yt_dlp

from src.ai_core.paths import BACKEND_DIR, MUSIC_DIR, ensure_output_dirs, unique_stem

logger = logging.getLogger(__name__)

MUSIC_DURATION = int(os.getenv("MUSIC_DURATION", 10))
SAMPLES_DIR = BACKEND_DIR / "assets" / "music_samples"

EMOTION_MUSIC_PROMPTS = {
    "sad": "slow melancholic piano, ambient, minor key, soft strings",
    "happy": "upbeat cinematic electronic music, bright synths, hopeful energy",
    "fearful": "dark ambient cinematic tension, eerie drones, suspense",
    "angry": "intense cinematic percussion, aggressive rhythm, dramatic strings",
    "surprised": "ethereal wonder, bright cinematic pads, magical atmosphere",
    "disgusted": "unsettling dark industrial ambient texture",
    "neutral": "calm ambient cinematic background music, soft pads",
}

EMOTION_SAMPLE_FILES = {
    "sad": "sad.mp3",
    "happy": "happy.mp3",
    "fearful": "fearful.mp3",
    "angry": "angry.mp3",
    "surprised": "surprised.mp3",
    "disgusted": "disgusted.mp3",
    "neutral": "neutral.mp3",
}


def get_music_prompt(emotion: str) -> str:
    return EMOTION_MUSIC_PROMPTS.get(emotion, EMOTION_MUSIC_PROMPTS["neutral"])


def _find_downloaded_file(stem: str) -> Optional[Path]:
    mp3_path = MUSIC_DIR / f"{stem}.mp3"
    if mp3_path.exists() and mp3_path.stat().st_size > 0:
        return mp3_path
    matches = sorted(MUSIC_DIR.glob(f"{stem}.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return next((path for path in matches if path.is_file() and path.stat().st_size > 0), None)


def _download_music_yt(query: str, stem: str) -> Optional[dict]:
    ensure_output_dirs()
    search_query = f"ytsearch1:{query} royalty free cinematic background music"
    logger.info("Downloading music with yt-dlp | query=%s", search_query)

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best ",
        "outtmpl": str(MUSIC_DIR / f"{stem}.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(search_query, download=True)

        downloaded = _find_downloaded_file(stem)
        if downloaded is None:
            raise RuntimeError(f"yt-dlp completed but no audio file was created for {stem}")

        logger.info("Music downloaded: %s (%s bytes)", downloaded, downloaded.stat().st_size)
        return {"music_path": str(downloaded), "source": "yt-dlp"}
    except Exception:
        logger.exception("yt-dlp music download failed")
        return None


def _copy_sample_music(emotion: str, stem: str) -> Optional[dict]:
    sample_name = EMOTION_SAMPLE_FILES.get(emotion, EMOTION_SAMPLE_FILES["neutral"])
    candidates = [
        SAMPLES_DIR / sample_name,
        MUSIC_DIR / sample_name,
    ]
    sample_path = next((path for path in candidates if path.exists()), None)
    if sample_path is None:
        return None

    out_path = MUSIC_DIR / f"{stem}.mp3"
    if sample_path.resolve() != out_path.resolve():
        shutil.copy2(sample_path, out_path)
    logger.info("Sample music selected: %s -> %s", sample_path, out_path)
    return {"music_path": str(out_path), "source": "sample"}


def generate_music(
    emotion: str,
    custom_prompt: Optional[str] = None,
    duration: int = MUSIC_DURATION,
    filename: Optional[str] = None,
) -> dict:
    """Download or select music and return a usable local audio path."""
    ensure_output_dirs()
    stem = filename or unique_stem("music")
    prompt = custom_prompt or get_music_prompt(emotion)

    logger.info(
        "Generating music | emotion=%s | duration=%ss | output_stem=%s",
        emotion,
        duration,
        stem,
    )
    logger.debug("Music prompt: %s", prompt)

    yt_result = _download_music_yt(prompt, stem)
    if yt_result:
        return {
            **yt_result,
            "emotion": emotion,
            "prompt": prompt,
            "duration": duration,
        }

    sample_result = _copy_sample_music(emotion, stem)
    if sample_result:
        return {
            **sample_result,
            "emotion": emotion,
            "prompt": prompt,
            "duration": duration,
        }

    logger.warning("No music source available for emotion=%s", emotion)
    return {
        "music_path": None,
        "emotion": emotion,
        "prompt": prompt,
        "duration": duration,
        "source": "none",
    }
