import logging
import os
from pathlib import Path
from typing import Literal, Optional

import numpy as np
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    afx,
)
from PIL import Image

from src.ai_core.paths import VIDEOS_DIR, ensure_output_dirs, unique_stem

logger = logging.getLogger(__name__)

OUTPUT_DIR = VIDEOS_DIR
ensure_output_dirs()

VIDEO_FPS = int(os.getenv("VIDEO_FPS", 24))
VIDEO_DURATION = int(os.getenv("VIDEO_DURATION", 8))

AnimationStyle = Literal["zoom_in", "zoom_out", "pan_left", "pan_right", "pulse", "ken_burns"]


# ───────── Animation Helpers ─────────

def _zoom_effect(clip: ImageClip, zoom_ratio: float = 0.04) -> ImageClip:
    return clip.resize(lambda t: 1 + zoom_ratio * t)


def _pan_effect(clip: ImageClip, direction: str = "left") -> ImageClip:
    w, h = clip.size
    extra = int(w * 0.15)

    def make_frame(t):
        frac = t / clip.duration
        x_offset = int(extra * frac) if direction == "left" else int(extra * (1 - frac))
        frame = np.array(clip.get_frame(t))
        return frame[:, x_offset: x_offset + w - extra]

    return clip.fl(lambda gf, t: make_frame(t), apply_to=["mask"])


def _pulse_effect(clip: ImageClip, intensity: float = 0.03) -> ImageClip:
    import math
    return clip.resize(lambda t: 1 + intensity * math.sin(2 * math.pi * t / 2))


def _ken_burns(clip: ImageClip) -> ImageClip:
    w, h = clip.size

    def transform(t):
        return 1 + 0.08 * (t / clip.duration)

    zoomed = clip.resize(transform)

    def crop_frame(get_frame, t):
        frame = get_frame(t)
        frac = t / clip.duration
        x_shift = int(w * 0.04 * frac)
        return frame[:h, x_shift: x_shift + w]

    return zoomed.fl(crop_frame)


ANIMATION_MAP = {
    "zoom_in": lambda c: _zoom_effect(c, 0.04),
    "zoom_out": lambda c: _zoom_effect(c, -0.03),
    "pan_left": lambda c: _pan_effect(c, "left"),
    "pan_right": lambda c: _pan_effect(c, "right"),
    "pulse": lambda c: _pulse_effect(c),
    "ken_burns": lambda c: _ken_burns(c),
}


EMOTION_ANIMATION = {
    "sad": "ken_burns",
    "happy": "zoom_in",
    "fearful": "pulse",
    "angry": "zoom_in",
    "surprised": "pan_left",
    "disgusted": "pulse",
    "neutral": "ken_burns",
}


# ───────── MAIN FUNCTION ─────────

def animate_image(
    image_path: str,
    emotion: str = "neutral",
    animation_style: Optional[AnimationStyle] = None,
    duration: int = VIDEO_DURATION,
    fps: int = VIDEO_FPS,
    audio_path: Optional[str] = None,
    filename: Optional[str] = None,
) -> dict:

    style = animation_style or EMOTION_ANIMATION.get(emotion, "ken_burns")

    clip = ImageClip(image_path).set_duration(duration)
    clip = ANIMATION_MAP.get(style, ANIMATION_MAP["ken_burns"])(clip)

    clip = clip.fadein(1).fadeout(1)

    # 🔥 AUTO AUDIO FIX + ATTACH
    if audio_path and Path(audio_path).exists():
        try:
            print("🎵 Audio path:", audio_path)

            audio = AudioFileClip(audio_path)

            # 🔥 convert to clean mp3
            audio.write_audiofile(
                "temp_fixed_audio.mp3",
                fps=44100,
                nbytes=2,
                codec="libmp3lame"
            )

            audio = AudioFileClip("temp_fixed_audio.mp3")

            # duration sync
            if audio.duration < duration:
                from moviepy.audio.fx.all import audio_loop
                audio = audio.fx(audio_loop, duration=duration)
            else:
                audio = audio.subclip(0, duration)

            audio = audio.set_fps(44100)
            audio = audio.audio_fadein(1).audio_fadeout(1.5)

            clip = clip.set_audio(audio)

            print("✅ Audio attached")

        except Exception as e:
            print("❌ Audio error:", e)

    fname = filename or unique_stem("video")
    out_path = OUTPUT_DIR / f"{fname}.mp4"

    clip.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        preset="fast",
    )

    clip.close()

    return {"video_path": str(out_path), "duration": duration}


# ───────── MERGE VIDEO + AUDIO ─────────

def merge_video_audio(video_path: str, audio_path: str, filename: Optional[str] = None) -> str:
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # 🔥 convert audio
    audio.write_audiofile(
        "temp_fixed_audio.mp3",
        fps=44100,
        nbytes=2,
        codec="libmp3lame"
    )

    audio = AudioFileClip("temp_fixed_audio.mp3")

    if audio.duration < video.duration:
        audio = audio.fx(afx.audio_loop, duration=video.duration)
    else:
        audio = audio.subclip(0, video.duration)

    audio = audio.set_fps(44100)
    final = video.set_audio(audio)

    fname = filename or unique_stem("video")
    out_path = OUTPUT_DIR / f"{fname}.mp4"

    final.write_videofile(
        str(out_path),
        codec="libx264",
        audio_codec="aac",
        fps=VIDEO_FPS,
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        preset="fast",
    )

    video.close()
    audio.close()
    final.close()

    return str(out_path)

