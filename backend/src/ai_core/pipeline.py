"""DreamScape master generation pipeline."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Literal, Optional

from src.ai_core import emotion as emotion_module
from src.ai_core import image_gen
from src.ai_core import prompt as prompt_module
from src.ai_core.music_gen import generate_music
from src.ai_core.video_fetch import get_video_from_pexels
from src.ai_core.video_gen import animate_image, merge_video_audio

logger = logging.getLogger(__name__)

ArtStyle = Literal[
    "photorealistic",
    "painterly",
    "anime",
    "cyberpunk",
    "van_gogh",
    "watercolor",
    "surrealist",
]
AnimationStyle = Literal["zoom_in", "zoom_out", "pan_left", "pan_right", "pulse", "ken_burns"]


@dataclass
class DreamRequest:
    text: str
    art_style: ArtStyle = "photorealistic"
    animation_style: Optional[AnimationStyle] = None
    image_steps: int = 30
    image_cfg: float = 7.5
    video_duration: int = 8
    seed: Optional[int] = None
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass
class DreamResult:
    request_id: str
    emotion: str
    confidence: float
    themes: list[str]
    prompt: str
    negative_prompt: str
    image_path: str
    video_path: str
    music_path: Optional[str]
    seed: int
    art_style: str
    music_source: str
    error: Optional[str] = None


class DreamPipeline:
    """Sequential flow: text -> emotion -> image/video -> music -> final merge."""

    def run(self, request: DreamRequest) -> DreamResult:
        rid = request.request_id
        logger.info("[%s] Pipeline started | text=%r", rid, request.text[:80])

        try:
            logger.info("[%s] Stage 1/6: emotion analysis", rid)
            analysis = emotion_module.analyze(request.text)
            emotion = analysis["emotion"]
            themes = analysis["themes"]
            confidence = analysis["confidence"]
            logger.info("[%s] Emotion=%s | confidence=%.3f | themes=%s", rid, emotion, confidence, themes)

            logger.info("[%s] Stage 2/6: prompt generation", rid)
            pos_prompt = prompt_module.build_prompt(
                emotion=emotion,
                themes=themes,
                art_style=request.art_style,
                user_text=request.text,
            )
            neg_prompt = prompt_module.build_negative_prompt(emotion)

            logger.info("[%s] Stage 3/6: image generation", rid)
            img_result = image_gen.generate_image(
                prompt=pos_prompt,
                negative_prompt=neg_prompt,
                steps=request.image_steps,
                guidance_scale=request.image_cfg,
                seed=request.seed,
                filename=f"img_{rid}",
            )
            image_path = img_result["image_path"]
            seed = img_result["seed"]
            logger.info("[%s] Image ready: %s", rid, image_path)

            logger.info("[%s] Stage 4/6: video generation", rid)
            query = f"{request.text} cinematic lighting 4k"
            try:
                raw_video_path = get_video_from_pexels(query)
            except Exception:
                logger.exception("[%s] Pexels fetch failed; using generated image animation", rid)
                raw_video = animate_image(
                    image_path=image_path,
                    emotion=emotion,
                    animation_style=request.animation_style,
                    duration=request.video_duration,
                    filename=f"raw_{rid}",
                )
                raw_video_path = raw_video["video_path"]
            logger.info("[%s] Source video ready: %s", rid, raw_video_path)

            logger.info("[%s] Stage 5/6: music generation/download", rid)
            music_result = generate_music(
                emotion=emotion,
                custom_prompt=f"{request.text}. {', '.join(themes)}. {emotion} cinematic background score",
                duration=request.video_duration,
                filename=f"music_{rid}",
            )
            music_path = music_result.get("music_path")
            music_source = music_result.get("source", "none")
            logger.info("[%s] Music source=%s | path=%s", rid, music_source, music_path)

            logger.info("[%s] Stage 6/6: merge final video", rid)
            if music_path:
                final_video_path = merge_video_audio(
                    raw_video_path,
                    music_path,
                    filename=f"final_{rid}",
                )
            else:
                logger.warning("[%s] No music available; final output is silent", rid)
                final_video_path = raw_video_path
            logger.info("[%s] Final video ready: %s", rid, final_video_path)

            return DreamResult(
                request_id=rid,
                emotion=emotion,
                confidence=confidence,
                themes=themes,
                prompt=pos_prompt,
                negative_prompt=neg_prompt,
                image_path=image_path,
                video_path=final_video_path,
                music_path=music_path,
                seed=seed,
                art_style=request.art_style,
                music_source=music_source,
            )

        except Exception as exc:
            logger.exception("[%s] Pipeline failed", rid)
            return DreamResult(
                request_id=rid,
                emotion="neutral",
                confidence=0.0,
                themes=[],
                prompt="",
                negative_prompt="",
                image_path="",
                video_path="",
                music_path=None,
                seed=0,
                art_style=request.art_style,
                music_source="none",
                error=str(exc),
            )


_pipeline_instance: Optional[DreamPipeline] = None


def get_pipeline() -> DreamPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DreamPipeline()
    return _pipeline_instance
