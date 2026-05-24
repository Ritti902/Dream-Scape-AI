"""
prompt.py — Dynamic Prompt Generator
DreamScape AI
"""

import logging
import os
import re
from typing import Optional

import openai

logger = logging.getLogger(__name__)

# ── Style mappings per emotion ─────────────────────────────────────────────────
EMOTION_STYLES: dict[str, dict] = {
    "sad": {
        "visual": "dark moody lighting, desaturated palette, soft rain, cinematic fog, melancholic",
        "atmosphere": "melancholic, introspective, ethereal",
        "lighting": "dim blue-grey light, overcast sky, subtle reflections",
        "color_palette": "muted blues, greys, deep purples",
    },
    "happy": {
        "visual": "vibrant warm colors, golden hour light, glowing bokeh, euphoric energy",
        "atmosphere": "joyful, uplifting, luminous",
        "lighting": "warm golden sunlight, soft lens flares, dappled light",
        "color_palette": "warm yellows, soft oranges, radiant whites",
    },
    "fearful": {
        "visual": "dark shadows, high contrast, dramatic tension, ominous atmosphere",
        "atmosphere": "tense, unsettling, mysterious",
        "lighting": "harsh underlighting, flickering, deep darkness",
        "color_palette": "deep blacks, sickly greens, cold whites",
    },
    "angry": {
        "visual": "intense reds, sharp edges, chaotic composition, explosive energy",
        "atmosphere": "powerful, turbulent, raw",
        "lighting": "harsh red-orange light, stark shadows",
        "color_palette": "fiery reds, burning oranges, charcoal blacks",
    },
    "surprised": {
        "visual": "surreal unexpected elements, vivid contrast, dreamlike distortions",
        "atmosphere": "surreal, wonder-filled, disorienting",
        "lighting": "dramatic reveal lighting, sudden bright flashes",
        "color_palette": "electric blues, vivid magentas, stark whites",
    },
    "disgusted": {
        "visual": "decay textures, murky greens, distorted forms, unsettling details",
        "atmosphere": "unnerving, visceral, otherworldly",
        "lighting": "sickly green tones, dim and murky",
        "color_palette": "murky greens, browns, desaturated flesh tones",
    },
    "neutral": {
        "visual": "balanced composition, soft diffused light, subtle dreamlike quality",
        "atmosphere": "calm, contemplative, balanced",
        "lighting": "soft natural light, gentle shadows",
        "color_palette": "muted earth tones, soft whites, subtle blues",
    },
}

ART_STYLES = {
    "photorealistic": "ultra-photorealistic, 8K, hyperdetailed, cinematic photography",
    "painterly": "oil painting style, impressionist brushwork, textured canvas",
    "anime": "anime art style, cel-shaded, vibrant, studio-quality illustration",
    "cyberpunk": "cyberpunk aesthetic, neon lights, futuristic dystopia, rain-slicked streets",
    "van_gogh": "Van Gogh style, swirling brushstrokes, post-impressionist, expressive",
    "watercolor": "delicate watercolor painting, soft washes, translucent layers",
    "surrealist": "Salvador Dali surrealism, dreamlike impossible architecture, melting reality",
}

BASE_SUFFIX = (
    "surreal dreamscape, ultra detailed, 4K resolution, award-winning digital art, "
    "trending on ArtStation, concept art"
)


def build_prompt(
    emotion: str,
    themes: list[str],
    art_style: str = "photorealistic",
    user_text: Optional[str] = None,
) -> str:
    """
    Build a Stable Diffusion prompt from emotion + themes.

    Args:
        emotion:    Primary emotion string (e.g. "sad")
        themes:     List of theme keywords (e.g. ["ocean", "silence"])
        art_style:  One of ART_STYLES keys
        user_text:  Original user input (used if GPT enrichment is enabled)

    Returns:
        A complete image generation prompt string.
    """
    style = EMOTION_STYLES.get(emotion, EMOTION_STYLES["neutral"])
    art = ART_STYLES.get(art_style, ART_STYLES["photorealistic"])

    theme_str = ", ".join(themes) if themes else "dreamscape"
    prompt = (
        f"{theme_str}, {style['visual']}, {style['atmosphere']}, "
        f"{style['lighting']}, {art}, {BASE_SUFFIX}"
    )

    # Optional: enrich with GPT
    if os.getenv("OPENAI_API_KEY") and user_text:
        try:
            prompt = _enrich_with_gpt(user_text, emotion, prompt)
        except Exception as e:
            logger.warning(f"GPT enrichment skipped: {e}")

    return prompt


def build_negative_prompt(emotion: str) -> str:
    """Return a negative prompt to suppress unwanted artifacts."""
    base_negative = (
        "blurry, low quality, pixelated, watermark, text, signature, "
        "ugly, deformed, extra limbs, bad anatomy, out of frame"
    )
    emotion_negative = {
        "happy": "dark, gloomy, horror, disturbing",
        "sad": "bright colors, cheerful, happy",
        "fearful": "cartoon, cute, childish",
        "angry": "calm, peaceful, soft",
    }
    extra = emotion_negative.get(emotion, "")
    return f"{base_negative}, {extra}".strip(", ")


def _enrich_with_gpt(user_text: str, emotion: str, base_prompt: str) -> str:
    """
    Use OpenAI GPT to enhance the base prompt with more artistic detail.
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_msg = (
        "You are an expert AI art director. Given a user's emotional description "
        "and a base image prompt, enhance the prompt to be more vivid, artistic, "
        "and cinematically beautiful. Return ONLY the enhanced prompt — no explanation."
    )
    user_msg = (
        f"User said: \"{user_text}\"\n"
        f"Emotion detected: {emotion}\n"
        f"Base prompt: {base_prompt}\n\n"
        "Create an enhanced, poetic image generation prompt:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=300,
        temperature=0.8,
    )

    enhanced = response.choices[0].message.content.strip()
    # strip markdown fences if any
    enhanced = re.sub(r"^```.*?\n|```$", "", enhanced, flags=re.DOTALL).strip()
    logger.info("GPT-enriched prompt generated.")
    return enhanced
