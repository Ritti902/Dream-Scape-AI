"""
emotion.py — Emotion + Theme Extraction Module
DreamScape AI
"""

from transformers import pipeline
import re
import logging

logger = logging.getLogger(__name__)

# ── Emotion classifier (lazy-loaded) ──────────────────────────────────────────
_emotion_pipeline = None

EMOTION_LABELS = {
    "sadness": "sad",
    "joy": "happy",
    "fear": "fearful",
    "anger": "angry",
    "surprise": "surprised",
    "disgust": "disgusted",
    "neutral": "neutral",
}

# Keyword categories for theme extraction
THEME_KEYWORDS = {
    "nature": ["ocean", "sea", "forest", "mountain", "sky", "river", "desert",
                "cave", "storm", "rain", "snow", "fire", "earth", "wind", "fog"],
    "time": ["night", "dawn", "dusk", "midnight", "twilight", "sunset", "sunrise",
              "ancient", "future", "past", "childhood", "memories"],
    "emotion": ["loneliness", "silence", "chaos", "peace", "pain", "hope",
                 "love", "loss", "freedom", "trapped", "searching"],
    "abstract": ["dreams", "infinity", "void", "light", "darkness", "shadow",
                  "mirror", "labyrinth", "portal", "spiral"],
    "urban": ["city", "street", "ruins", "tower", "bridge", "underground", "neon"],
}


def _get_emotion_pipeline():
    """Lazy-load the HuggingFace emotion model."""
    global _emotion_pipeline
    if _emotion_pipeline is None:
        logger.info("Loading emotion model...")
        _emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
        )
    return _emotion_pipeline


def extract_emotion(text: str) -> dict:
    """
    Run emotion classification on input text.

    Returns:
        {
            "primary_emotion": "sad",
            "confidence": 0.87,
            "all_emotions": {"sad": 0.87, "joy": 0.05, ...}
        }
    """
    try:
        classifier = _get_emotion_pipeline()
        results = classifier(text[:512])  # model max length guard

        # results[0] is a list of {label, score} dicts
        scores = {
            EMOTION_LABELS.get(r["label"].lower(), r["label"].lower()): round(r["score"], 4)
            for r in results[0]
        }

        primary = max(scores, key=scores.get)
        return {
            "primary_emotion": primary,
            "confidence": scores[primary],
            "all_emotions": scores,
        }

    except Exception as e:
        logger.error(f"Emotion extraction failed: {e}")
        return {
            "primary_emotion": "neutral",
            "confidence": 1.0,
            "all_emotions": {"neutral": 1.0},
        }


def extract_themes(text: str) -> list[str]:
    """
    Extract relevant visual/conceptual themes from user text.

    Returns a list of theme keywords found in the input.
    """
    text_lower = text.lower()
    found_themes = []

    for category, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            # whole-word match
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                found_themes.append(kw)

    # Fallback: extract meaningful nouns if no themes found
    if not found_themes:
        words = re.findall(r"\b[a-z]{4,}\b", text_lower)
        stop = {"that", "this", "with", "have", "from", "they", "will",
                "what", "when", "your", "about", "feel", "like", "just"}
        found_themes = [w for w in words if w not in stop][:5]

    return list(dict.fromkeys(found_themes))  # deduplicate, preserve order


def analyze(text: str) -> dict:
    """
    Full analysis: emotion + themes combined.

    Returns:
        {
            "emotion": "sad",
            "confidence": 0.87,
            "themes": ["ocean", "silence", "night"],
            "all_emotions": {...}
        }
    """
    emotion_data = extract_emotion(text)
    themes = extract_themes(text)

    return {
        "emotion": emotion_data["primary_emotion"],
        "confidence": emotion_data["confidence"],
        "themes": themes,
        "all_emotions": emotion_data["all_emotions"],
    }