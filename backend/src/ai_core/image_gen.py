"""
image_gen.py — Image Generation Module (Stable Diffusion)
DreamScape AI
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

import torch
from diffusers import (
    DPMSolverMultistepScheduler,
    StableDiffusionPipeline,
)
from PIL import Image

from src.ai_core.paths import IMAGES_DIR, ensure_output_dirs, unique_stem

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
DEFAULT_MODEL = os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5")
OUTPUT_DIR = IMAGES_DIR
ensure_output_dirs()

# Image dimensions — must be multiples of 8
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", 768))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", 512))

# Generation defaults
DEFAULT_STEPS = int(os.getenv("SD_STEPS", 30))
DEFAULT_CFG = float(os.getenv("SD_CFG", 7.5))


# ── Pipeline (lazy-loaded, singleton) ─────────────────────────────────────────
_pipe: Optional[StableDiffusionPipeline] = None


def _get_pipeline() -> StableDiffusionPipeline:
    global _pipe
    if _pipe is not None:
        return _pipe

    logger.info(f"Loading Stable Diffusion model: {DEFAULT_MODEL}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    _pipe = StableDiffusionPipeline.from_pretrained(
        DEFAULT_MODEL,
        torch_dtype=dtype,
        safety_checker=None,          # disable for dream art use case
        requires_safety_checker=False,
    )

    # Faster sampler
    _pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        _pipe.scheduler.config
    )

    _pipe = _pipe.to(device)

    # Memory optimizations
    if device == "cuda":
        _pipe.enable_attention_slicing()
        try:
            _pipe.enable_xformers_memory_efficient_attention()
            logger.info("xFormers memory-efficient attention enabled.")
        except Exception:
            logger.info("xFormers not available — skipping.")

    logger.info(f"Pipeline ready on {device}.")
    return _pipe


def generate_image(
    prompt: str,
    negative_prompt: str = "",
    steps: int = DEFAULT_STEPS,
    guidance_scale: float = DEFAULT_CFG,
    seed: Optional[int] = None,
    width: int = IMAGE_WIDTH,
    height: int = IMAGE_HEIGHT,
    filename: Optional[str] = None,
) -> dict:
    """
    Generate a dream image from a prompt.

    Args:
        prompt:          Positive prompt string
        negative_prompt: Negative prompt string
        steps:           Denoising steps (higher = better quality, slower)
        guidance_scale:  CFG scale (7–9 recommended)
        seed:            RNG seed for reproducibility (None = random)
        width:           Output image width
        height:          Output image height
        filename:        Custom output filename (without extension)

    Returns:
        {
            "image_path": "outputs/images/dream_abc123.png",
            "seed": 42,
            "prompt": "...",
            "width": 768,
            "height": 512,
        }
    """
    pipe = _get_pipeline()

    # Seed handling
    generator = None
    if seed is not None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        generator = torch.Generator(device=device).manual_seed(seed)
    else:
        seed = torch.randint(0, 2**32 - 1, (1,)).item()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        generator = torch.Generator(device=device).manual_seed(seed)

    logger.info(f"Generating image | seed={seed} | steps={steps} | CFG={guidance_scale}")
    logger.debug(f"Prompt: {prompt[:120]}...")

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt or None,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        generator=generator,
        width=width,
        height=height,
    )

    image: Image.Image = result.images[0]

    # Save
    fname = filename or unique_stem("img")
    image_path = OUTPUT_DIR / f"{fname}.png"
    image.save(str(image_path))
    logger.info(f"Image saved: {image_path}")

    return {
        "image_path": str(image_path),
        "seed": seed,
        "prompt": prompt,
        "width": width,
        "height": height,
    }


def unload_pipeline() -> None:
    """Release GPU memory by unloading the pipeline."""
    global _pipe
    if _pipe is not None:
        del _pipe
        _pipe = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Image generation pipeline unloaded.")






