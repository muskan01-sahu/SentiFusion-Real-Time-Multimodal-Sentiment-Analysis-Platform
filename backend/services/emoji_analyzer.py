"""
Emoji Sentiment Analyzer
Scores emojis using a curated sentiment lexicon.
Produces per-emoji scores and an aggregate sentiment.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EmojiSentimentResult:
    label: str          # positive / negative / neutral
    score: float        # overall confidence
    emoji_scores: dict  # per-emoji scores
    emojis_found: list[str]


# ─── Emoji Sentiment Lexicon ─────────────────────────────────────────────────
# Scores: -1.0 (very negative) to +1.0 (very positive)

EMOJI_LEXICON: dict[str, float] = {
    # Strongly Positive
    "😊": 0.95, "😍": 0.95, "🥰": 0.98, "😄": 0.90, "😁": 0.88,
    "🤩": 0.95, "🎉": 0.92, "🥳": 0.92, "✨": 0.80, "💫": 0.78,
    "❤️": 0.95, "💕": 0.93, "💖": 0.95, "💗": 0.94, "💓": 0.92,
    "🔥": 0.80, "🚀": 0.85, "💪": 0.82, "👏": 0.88, "🙌": 0.90,
    "😂": 0.70, "🤣": 0.70, "😆": 0.75, "😀": 0.88, "😃": 0.87,
    "🌟": 0.82, "⭐": 0.78, "🌈": 0.80, "🎊": 0.90, "🎶": 0.72,
    "👍": 0.80, "🤝": 0.75, "💯": 0.88, "✅": 0.78, "🏆": 0.90,
    "🌸": 0.72, "🌺": 0.70, "🌻": 0.72, "🌹": 0.74, "💐": 0.75,
    "🎯": 0.70, "💡": 0.65, "🎁": 0.78, "🙏": 0.68, "😇": 0.80,
    "🤗": 0.88, "😎": 0.72, "😏": 0.40, "😋": 0.70, "🤤": 0.60,
    # Negative
    "😡": -0.95, "😤": -0.88, "🤬": -0.98, "😠": -0.90, "💢": -0.85,
    "😭": -0.80, "😢": -0.85, "😞": -0.80, "😔": -0.78, "😟": -0.75,
    "💔": -0.90, "😰": -0.75, "😨": -0.80, "😱": -0.82, "🤢": -0.88,
    "🤮": -0.95, "🖕": -0.98, "👎": -0.85, "❌": -0.78, "🚫": -0.72,
    "😒": -0.68, "🙄": -0.65, "😑": -0.62, "😐": -0.10, "😓": -0.65,
    "💀": -0.70, "☠️": -0.72, "👻": -0.30, "😈": -0.68, "🤡": -0.55,
    "🥺": -0.55, "😿": -0.80, "🙍": -0.65, "😩": -0.80, "😫": -0.78,
    # Neutral / Context-Dependent
    "🤔": 0.05, "🧐": 0.05, "😶": 0.0, "🤷": 0.0, "😕": -0.30,
    "👀": 0.10, "🤭": 0.25, "😳": -0.20, "🥴": -0.25, "😴": -0.10,
    "💤": -0.15, "🌚": -0.20, "🌝": 0.15, "🤫": 0.10, "🧠": 0.30,
    "📊": 0.15, "📈": 0.50, "📉": -0.40, "💰": 0.55, "💸": -0.50,
}

# Intensity multipliers for repeated emojis
INTENSITY_BOOST = {1: 1.0, 2: 1.15, 3: 1.25}


def get_intensity_multiplier(count: int) -> float:
    return INTENSITY_BOOST.get(count, 1.30)


def score_to_label(score: float) -> str:
    if score > 0.15:
        return "positive"
    elif score < -0.15:
        return "negative"
    return "neutral"


def analyze_emoji_sentiment(emojis: list[str]) -> EmojiSentimentResult:
    """
    Analyze sentiment from a list of emojis.
    Returns per-emoji scores and an aggregate result.
    """
    if not emojis:
        return EmojiSentimentResult(
            label="neutral",
            score=0.5,
            emoji_scores={},
            emojis_found=[],
        )

    # Count emoji frequencies
    from collections import Counter
    emoji_counts = Counter(emojis)

    per_emoji_scores = {}
    weighted_scores = []

    for em, count in emoji_counts.items():
        base_score = EMOJI_LEXICON.get(em, None)
        if base_score is None:
            # Unknown emoji — try unicode category check
            try:
                import unicodedata
                name = unicodedata.name(em, "").lower()
                if any(w in name for w in ["smile", "happy", "joy", "heart", "love"]):
                    base_score = 0.60
                elif any(w in name for w in ["sad", "cry", "angry", "frown"]):
                    base_score = -0.60
                else:
                    base_score = 0.0
            except Exception:
                base_score = 0.0

        intensity = get_intensity_multiplier(count)
        final_score = base_score * intensity
        per_emoji_scores[em] = round(final_score, 4)
        weighted_scores.append(final_score)

    # Aggregate: weighted mean with bias toward extremes
    if weighted_scores:
        avg = sum(weighted_scores) / len(weighted_scores)
        # Normalize to 0–1 confidence scale
        normalized_confidence = (avg + 1.0) / 2.0
        label = score_to_label(avg)

        # Confidence: how far from 0.5 (neutral baseline)
        confidence = abs(normalized_confidence - 0.5) * 2
        confidence = min(max(confidence + 0.3, 0.3), 0.99)
    else:
        avg = 0.0
        label = "neutral"
        confidence = 0.5

    return EmojiSentimentResult(
        label=label,
        score=round(confidence, 4),
        emoji_scores=per_emoji_scores,
        emojis_found=list(emoji_counts.keys()),
    )
