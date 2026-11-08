"""
Text Sentiment Analyzer
Uses cardiffnlp/twitter-roberta-base-sentiment-latest (primary)
Plus DistilBERT and BERT for model comparison.
"""

import logging
import re
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import transformers — fallback to mock if not installed
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("⚠️  transformers not installed — using mock sentiment")


@dataclass
class TextSentimentResult:
    label: str           # positive / negative / neutral
    score: float         # confidence 0–1
    scores: dict         # all class scores
    model_comparison: dict  # scores from each model


# ─── Model Cache (lazy-loaded) ───────────────────────────────────────────────

_models: dict = {}

MODEL_CONFIGS = {
    "roberta": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "distilbert": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    "bert": "nlptown/bert-base-multilingual-uncased-sentiment",
}

LABEL_MAP = {
    # RoBERTa labels
    "positive": "positive", "negative": "negative", "neutral": "neutral",
    # NLPTown 1-5 star mapping
    "1 star": "negative", "2 stars": "negative",
    "3 stars": "neutral",
    "4 stars": "positive", "5 stars": "positive",
    # Generic
    "POSITIVE": "positive", "NEGATIVE": "negative", "NEUTRAL": "neutral",
    "LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive",
}


def _load_pipeline(model_key: str):
    """Lazy-load a HuggingFace pipeline."""
    if model_key in _models:
        return _models[model_key]

    model_name = MODEL_CONFIGS[model_key]
    logger.info(f"Loading model: {model_name}")
    try:
        pipe = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            return_all_scores=True,
            device=-1,  # CPU
        )
        _models[model_key] = pipe
        logger.info(f"✅ Loaded {model_key}")
        return pipe
    except Exception as e:
        logger.error(f"Failed to load {model_key}: {e}")
        return None


def clean_text(text: str) -> str:
    """Clean tweet text for model input."""
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # Remove @mentions
    text = re.sub(r"@\w+", "@user", text)
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate to 512 tokens worth (~400 chars to be safe)
    return text[:512]


def _normalize_scores(raw_scores: list) -> dict:
    """Convert raw pipeline output to {positive, negative, neutral} dict."""
    result = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    for item in raw_scores:
        label = LABEL_MAP.get(item["label"], item["label"].lower())
        if label in result:
            result[label] = max(result[label], item["score"])
    return result


def _mock_sentiment(text: str) -> dict:
    """Rule-based fallback for when transformers aren't available."""
    text_lower = text.lower()
    pos_words = ["great", "amazing", "love", "happy", "excited", "wonderful", "excellent", "fantastic", "good", "awesome", "best", "🚀", "😊", "🔥", "❤️"]
    neg_words = ["hate", "terrible", "awful", "bad", "worst", "horrible", "disgusting", "broken", "failed", "😡", "😤", "💔", "😭"]

    pos_score = sum(1 for w in pos_words if w in text_lower)
    neg_score = sum(1 for w in neg_words if w in text_lower)

    total = pos_score + neg_score + 1
    if pos_score > neg_score:
        return {"positive": pos_score/total + 0.4, "negative": neg_score/total + 0.1, "neutral": 0.1}
    elif neg_score > pos_score:
        return {"positive": pos_score/total + 0.1, "negative": neg_score/total + 0.4, "neutral": 0.1}
    else:
        return {"positive": 0.25, "negative": 0.25, "neutral": 0.5}


def _infer_single_model(model_key: str, text: str) -> Optional[dict]:
    """Run inference with one model and return normalized scores."""
    if not TRANSFORMERS_AVAILABLE:
        return _mock_sentiment(text)

    pipe = _load_pipeline(model_key)
    if pipe is None:
        return _mock_sentiment(text)

    try:
        raw = pipe(text)
        # pipeline returns list of list of dicts when return_all_scores=True
        if isinstance(raw[0], list):
            return _normalize_scores(raw[0])
        return _normalize_scores(raw)
    except Exception as e:
        logger.error(f"Inference error ({model_key}): {e}")
        return _mock_sentiment(text)


def analyze_text_sentiment(text: str) -> TextSentimentResult:
    """
    Main text analysis function.
    Runs RoBERTa (primary) + DistilBERT + BERT for comparison.
    """
    cleaned = clean_text(text)

    # Primary model: RoBERTa
    roberta_scores = _infer_single_model("roberta", cleaned)

    # Secondary models for comparison
    distilbert_scores = _infer_single_model("distilbert", cleaned)
    bert_scores = _infer_single_model("bert", cleaned)

    # Final result = RoBERTa (highest quality for Twitter)
    final_label = max(roberta_scores, key=roberta_scores.get)
    final_score = roberta_scores[final_label]

    # Normalize so all scores sum to 1
    total = sum(roberta_scores.values())
    normalized = {k: round(v/total, 4) for k, v in roberta_scores.items()} if total > 0 else roberta_scores

    model_comparison = {
        "roberta": round(roberta_scores.get(final_label, 0), 4),
        "distilbert": round(distilbert_scores.get(final_label, 0) if distilbert_scores else 0, 4),
        "bert": round(bert_scores.get(final_label, 0) if bert_scores else 0, 4),
    }

    return TextSentimentResult(
        label=final_label,
        score=round(final_score, 4),
        scores=normalized,
        model_comparison=model_comparison,
    )
