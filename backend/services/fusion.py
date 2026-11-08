"""
Multimodal Fusion Service
Combines text, emoji, and image sentiment into a final prediction.
Uses a weighted confidence-based fusion strategy.

Architecture:
  text_score (RoBERTa, weight 0.55)
  + emoji_score (Lexicon, weight 0.25)
  + image_score (ViT, weight 0.20)
  → Weighted average → Final sentiment + confidence

Sarcasm Detection:
  A simple rule-based detector adjusts confidence when
  positive text co-occurs with negative context patterns.
"""

import logging
import re
from dataclasses import dataclass

from services.text_analyzer import TextSentimentResult
from services.emoji_analyzer import EmojiSentimentResult
from services.image_analyzer import ImageSentimentResult

logger = logging.getLogger(__name__)

# ─── Fusion Weights ───────────────────────────────────────────────────────────
# Adjust these based on your experimental results for the research paper

WEIGHTS = {
    "text": 0.55,
    "emoji": 0.25,
    "image": 0.20,
}

# Lower image weight when no image is present (redistribute to text)
WEIGHTS_NO_IMAGE = {
    "text": 0.70,
    "emoji": 0.30,
    "image": 0.0,
}

# Lower emoji weight when no emojis present
WEIGHTS_NO_EMOJI = {
    "text": 0.75,
    "emoji": 0.0,
    "image": 0.25,
}

WEIGHTS_TEXT_ONLY = {
    "text": 1.0,
    "emoji": 0.0,
    "image": 0.0,
}


@dataclass
class FusionResult:
    final_sentiment: str        # positive / negative / neutral
    confidence: float           # 0–1
    label: str                  # "Positive" (capitalized for display)
    breakdown: dict             # per-modality results
    model_comparison: dict      # roberta/distilbert/bert scores
    sarcasm: dict               # { detected: bool, score: float }
    fusion_weights: dict        # weights actually used
    language: str


# ─── Sarcasm Detection ────────────────────────────────────────────────────────

SARCASM_PATTERNS = [
    r"\bsure(ly)?\b.*\bgreat\b",
    r"\byeah right\b",
    r"\boh really\b",
    r"\bwow thanks\b.*\bso helpful\b",
    r"\bgreat job\b.*💀",
    r"\bso helpful\b",
    r"\bwhat a surprise\b",
    r"\bshocking\b.*😐",
    r"\blovely\b.*💀",
    r"\bgeniuses\b",
    r"\btotally\b.*not",
    r"\bnot at all\b.*😊",
]

SARCASM_EMOJI_PAIRS = [
    ("😊", "💀"), ("🔥", "💀"), ("😍", "💀"),
    ("👏", "💀"), ("✅", "❌"), ("😂", "😡"),
]


def detect_sarcasm(text: str, emojis: list[str], text_label: str, emoji_label: str) -> dict:
    """
    Lightweight sarcasm detector.
    Checks for linguistic patterns + contradictory emoji combinations.
    """
    text_lower = text.lower()
    sarcasm_score = 0.0

    # Pattern matching
    for pattern in SARCASM_PATTERNS:
        if re.search(pattern, text_lower):
            sarcasm_score += 0.20

    # Contradictory emoji pairs
    for pos_em, neg_em in SARCASM_EMOJI_PAIRS:
        if pos_em in emojis and neg_em in emojis:
            sarcasm_score += 0.25

    # Text–emoji contradiction
    if text_label == "positive" and emoji_label == "negative":
        sarcasm_score += 0.15
    if text_label == "negative" and emoji_label == "positive":
        sarcasm_score += 0.10

    sarcasm_score = min(sarcasm_score, 1.0)
    return {
        "detected": sarcasm_score > 0.35,
        "score": round(sarcasm_score, 4),
    }


# ─── Language Detection ───────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect language. Returns ISO 639-1 code."""
    try:
        from langdetect import detect
        lang = detect(text)
        # Hinglish heuristic: Hindi script present + Latin characters
        hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        if lang == "hi" or (hindi_chars > 3):
            return "hi"
        if lang in ("en", "hi"):
            return lang
        return lang
    except Exception:
        return "en"


# ─── Fusion Logic ─────────────────────────────────────────────────────────────

def _sentiment_to_score(label: str, confidence: float) -> dict:
    """Convert label + confidence to signed component score."""
    direction = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}.get(label, 0.0)
    return {
        "positive": confidence if label == "positive" else max(0, (1 - confidence) * 0.3),
        "negative": confidence if label == "negative" else max(0, (1 - confidence) * 0.3),
        "neutral": confidence if label == "neutral" else max(0, (1 - confidence) * 0.4),
    }


def fuse_sentiments(
    text_result: TextSentimentResult,
    emoji_result: EmojiSentimentResult,
    image_result: ImageSentimentResult,
    emojis: list[str],
    language: str = "en",
) -> FusionResult:
    """
    Combine text, emoji, and image sentiment into a final prediction.
    """
    has_image = image_result.analyzed and image_result.method not in ("no_image", "fetch_failed")
    has_emoji = bool(emojis)

    # Select appropriate weights
    if has_image and has_emoji:
        weights = WEIGHTS
    elif not has_image and has_emoji:
        weights = WEIGHTS_NO_IMAGE
    elif has_image and not has_emoji:
        weights = WEIGHTS_NO_EMOJI
    else:
        weights = WEIGHTS_TEXT_ONLY

    # Build combined scores across classes
    combined = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    # Text contribution
    for cls, score in text_result.scores.items():
        combined[cls] += score * weights["text"]

    # Emoji contribution
    if has_emoji:
        for cls in combined:
            emoji_cls_score = 1.0 if emoji_result.label == cls else (0.1 if cls == "neutral" else 0.0)
            combined[cls] += emoji_cls_score * emoji_result.score * weights["emoji"]

    # Image contribution
    if has_image:
        for cls, score in image_result.scores.items():
            combined[cls] += score * weights["image"]

    # Normalize
    total = sum(combined.values()) or 1
    normalized = {k: round(v / total, 4) for k, v in combined.items()}

    final_label = max(normalized, key=normalized.get)
    confidence = normalized[final_label]

    # Sarcasm check — adjust confidence
    sarcasm = detect_sarcasm(
        text="",  # Pass actual tweet text from caller if available
        emojis=emojis,
        text_label=text_result.label,
        emoji_label=emoji_result.label,
    )
    if sarcasm["detected"]:
        # Flip label toward opposite
        if final_label == "positive":
            confidence *= 0.6
            if confidence < 0.45:
                final_label = "negative"
                confidence = 0.55
        logger.info(f"⚠️  Sarcasm detected (score={sarcasm['score']})")

    return FusionResult(
        final_sentiment=final_label,
        confidence=round(confidence, 4),
        label=final_label.capitalize(),
        breakdown={
            "text": {
                "label": text_result.label,
                "score": round(text_result.score, 4),
                "scores": text_result.scores,
            },
            "emoji": {
                "label": emoji_result.label,
                "score": round(emoji_result.score, 4),
                "emoji_scores": emoji_result.emoji_scores,
                "emojis_found": emoji_result.emojis_found,
            },
            "image": {
                "label": image_result.label,
                "score": round(image_result.score, 4),
                "analyzed": image_result.analyzed,
                "method": image_result.method,
            },
        },
        model_comparison=text_result.model_comparison,
        sarcasm=sarcasm,
        fusion_weights=weights,
        language=language,
    )
