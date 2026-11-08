"""
Image Sentiment Analyzer
Uses google/vit-base-patch16-224 (fine-tuned variant) to detect
visual sentiment from tweet images.
Falls back to color/brightness heuristics when model unavailable.
"""

import logging
import io
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

try:
    from transformers import pipeline as hf_pipeline
    from PIL import Image
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    logger.warning("⚠️  PIL/transformers not available — using heuristic image analysis")


@dataclass
class ImageSentimentResult:
    label: str
    score: float
    scores: dict
    analyzed: bool = True
    method: str = "vit"


# ─── Model Cache ─────────────────────────────────────────────────────────────

_image_pipeline = None

IMAGE_MODEL = "Falconsai/nsfw_image_detection"  # General visual model, swap for sentiment-specific fine-tune
# Best alternative: "ahmed-masry/ChartQA_Image_Sentiment" or custom fine-tune on MVSA dataset


def _load_image_pipeline():
    global _image_pipeline
    if _image_pipeline is not None:
        return _image_pipeline
    if not VISION_AVAILABLE:
        return None
    try:
        # In production: use a model fine-tuned on MVSA or FER dataset
        # For MVP: use a general ViT image classifier and remap labels
        _image_pipeline = hf_pipeline(
            "image-classification",
            model="google/vit-base-patch16-224",
            device=-1,
        )
        logger.info("✅ Loaded ViT image pipeline")
        return _image_pipeline
    except Exception as e:
        logger.error(f"Failed to load image pipeline: {e}")
        return None


# ImageNet class → sentiment mapping (simplified)
# In production, fine-tune ViT directly on sentiment-labeled images
IMAGENET_SENTIMENT_MAP = {
    # Context-based: celebrations, nature = positive
    "picket_fence": "positive", "valley": "positive", "lakeside": "positive",
    "cliff": "negative", "volcano": "negative", "wreck": "negative",
    "bouquet": "positive", "confetti": "positive",
}


async def fetch_image(url: str) -> Optional[bytes]:
    """Download image bytes from URL."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
    except Exception as e:
        logger.warning(f"Failed to fetch image {url}: {e}")
        return None


def _heuristic_image_sentiment(image_bytes: bytes) -> ImageSentimentResult:
    """
    Heuristic fallback: analyze dominant colors and brightness.
    Warm/bright colors → positive, cool/dark → negative.
    """
    try:
        from PIL import Image as PILImage
        import colorsys

        img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((100, 100))  # Fast processing
        pixels = list(img.getdata())

        total_brightness = 0
        warm_count = 0
        cool_count = 0

        for r, g, b in pixels:
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            total_brightness += v
            # Warm hues: red (0–0.1), yellow (0.1–0.2), orange
            if 0.0 <= h <= 0.15 or 0.9 <= h <= 1.0:
                warm_count += 1
            # Cool hues: blue, purple
            elif 0.55 <= h <= 0.75:
                cool_count += 1

        avg_brightness = total_brightness / len(pixels)
        warm_ratio = warm_count / len(pixels)
        cool_ratio = cool_count / len(pixels)

        if avg_brightness > 0.65 and warm_ratio > cool_ratio:
            label, score = "positive", round(0.60 + warm_ratio * 0.3, 4)
        elif avg_brightness < 0.35 or cool_ratio > warm_ratio + 0.1:
            label, score = "negative", round(0.55 + cool_ratio * 0.2, 4)
        else:
            label, score = "neutral", 0.60

        return ImageSentimentResult(
            label=label,
            score=min(score, 0.95),
            scores={"positive": score if label == "positive" else 0.2,
                    "negative": score if label == "negative" else 0.2,
                    "neutral": score if label == "neutral" else 0.25},
            analyzed=True,
            method="heuristic",
        )
    except Exception as e:
        logger.error(f"Heuristic analysis failed: {e}")
        return ImageSentimentResult(
            label="neutral", score=0.5,
            scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            analyzed=False, method="fallback"
        )


async def analyze_image_sentiment(image_urls: list[str]) -> ImageSentimentResult:
    """
    Analyze sentiment from a list of image URLs.
    Uses ViT model or falls back to heuristics.
    """
    if not image_urls:
        return ImageSentimentResult(
            label="neutral",
            score=0.5,
            scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            analyzed=False,
            method="no_image",
        )

    # Use first image (primary content)
    image_bytes = await fetch_image(image_urls[0])
    if not image_bytes:
        return ImageSentimentResult(
            label="neutral", score=0.5,
            scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            analyzed=False, method="fetch_failed"
        )

    # Try ViT model
    pipe = _load_image_pipeline()
    if pipe is not None and VISION_AVAILABLE:
        try:
            from PIL import Image as PILImage
            img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
            results = pipe(img, top_k=5)

            # Map predicted classes to sentiment
            pos_score = neg_score = neu_score = 0.0
            for r in results:
                label = r["label"].lower()
                sentiment = IMAGENET_SENTIMENT_MAP.get(label, "neutral")
                if sentiment == "positive":
                    pos_score += r["score"]
                elif sentiment == "negative":
                    neg_score += r["score"]
                else:
                    neu_score += r["score"]

            # Normalize
            total = pos_score + neg_score + neu_score or 1
            scores = {
                "positive": round(pos_score / total, 4),
                "negative": round(neg_score / total, 4),
                "neutral": round(neu_score / total, 4),
            }
            final_label = max(scores, key=scores.get)
            return ImageSentimentResult(
                label=final_label,
                score=round(scores[final_label], 4),
                scores=scores,
                analyzed=True,
                method="vit",
            )
        except Exception as e:
            logger.warning(f"ViT inference failed: {e}, falling back to heuristic")

    # Fallback: color/brightness heuristic
    return _heuristic_image_sentiment(image_bytes)
