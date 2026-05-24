"""
schemas.py — Pydantic Request / Response Schemas
DreamScape AI
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ── Enums ──────────────────────────────────────────────────────────────────────
ArtStyle = Literal[
    "photorealistic", "painterly", "anime",
    "cyberpunk", "van_gogh", "watercolor", "surrealist"
]

AnimationStyle = Literal[
    "zoom_in", "zoom_out", "pan_left",
    "pan_right", "pulse", "ken_burns"
]


# ── Request Schemas ────────────────────────────────────────────────────────────

class GenerateDreamRequest(BaseModel):
    """POST /generate — body schema."""
    text: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="User's dream description or emotional input",
        examples=["I feel lost in an endless ocean of silence"],
    )
    art_style: ArtStyle = Field(
        default="photorealistic",
        description="Visual art style for the generated image",
    )
    animation_style: Optional[AnimationStyle] = Field(
        default=None,
        description="Animation effect for the video (None = auto-select based on emotion)",
    )
    image_steps: int = Field(
        default=30,
        ge=10,
        le=100,
        description="Number of diffusion steps (higher = better quality, slower)",
    )
    image_cfg: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Classifier-free guidance scale",
    )
    video_duration: int = Field(
        default=8,
        ge=3,
        le=30,
        description="Output video length in seconds",
    )
    seed: Optional[int] = Field(
        default=None,
        ge=0,
        description="RNG seed for reproducible results (None = random)",
    )

    @field_validator("text")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class AnalyzeRequest(BaseModel):
    """POST /analyze — analyze emotion only (no generation)."""
    text: str = Field(..., min_length=3, max_length=1000)


# ── Response Schemas ───────────────────────────────────────────────────────────

class EmotionResult(BaseModel):
    emotion: str
    confidence: float
    themes: list[str]
    all_emotions: dict[str, float]


class GenerateDreamResponse(BaseModel):
    request_id: str
    emotion: str
    confidence: float
    themes: list[str]
    prompt: str
    image_url: str
    video_url: str
    music_url: Optional[str]
    seed: int
    art_style: str
    music_source: str
    error: Optional[str] = None


class AnalyzeResponse(BaseModel):
    emotion: str
    confidence: float
    themes: list[str]
    all_emotions: dict[str, float]
    suggested_art_style: str
    music_prompt: str


class HealthResponse(BaseModel):
    status: str
    version: str
    gpu_available: bool
    models_loaded: list[str]


class ErrorResponse(BaseModel):
    detail: str
    request_id: Optional[str] = None

    