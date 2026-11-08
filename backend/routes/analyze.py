"""
/api/analyze — Main Analysis Endpoint
Orchestrates the full multimodal sentiment analysis pipeline.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_db, AnalysisRecord
from services.tweet_scraper import scrape_tweet
from services.text_analyzer import analyze_text_sentiment
from services.emoji_analyzer import analyze_emoji_sentiment
from services.image_analyzer import analyze_image_sentiment
from services.fusion import fuse_sentiments, detect_language

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    tweet_url: str
    include_replies: bool = False


class AnalyzeResponse(BaseModel):
    analysis_id: str
    tweet_data: dict
    sentiment: dict
    model_comparison: dict
    sarcasm: dict
    language: str
    fusion_weights: dict
    processing_time_ms: int


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_tweet(
    req: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Full multimodal sentiment analysis pipeline:
    1. Scrape tweet
    2. Analyze text (RoBERTa)
    3. Analyze emojis (Lexicon)
    4. Analyze images (ViT)
    5. Fuse results
    6. Store in DB
    """
    import time
    start_time = time.time()
    analysis_id = str(uuid.uuid4())

    logger.info(f"[{analysis_id}] Starting analysis for: {req.tweet_url}")

    # ── Step 1: Fetch Tweet ────────────────────────────────────────────────
    try:
        tweet = await scrape_tweet(req.tweet_url)
        logger.info(f"[{analysis_id}] Tweet fetched: '{tweet.text[:60]}...'")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[{analysis_id}] Scrape error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tweet: {str(e)}")

    # ── Step 2: Language Detection ─────────────────────────────────────────
    language = detect_language(tweet.text)
    logger.info(f"[{analysis_id}] Language: {language}")

    # ── Step 3: Text Analysis ──────────────────────────────────────────────
    try:
        text_result = analyze_text_sentiment(tweet.text)
        logger.info(f"[{analysis_id}] Text: {text_result.label} ({text_result.score:.3f})")
    except Exception as e:
        logger.error(f"[{analysis_id}] Text analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

    # ── Step 4: Emoji Analysis ─────────────────────────────────────────────
    try:
        emoji_result = analyze_emoji_sentiment(tweet.emojis)
        logger.info(f"[{analysis_id}] Emoji: {emoji_result.label} ({emoji_result.score:.3f})")
    except Exception as e:
        logger.error(f"[{analysis_id}] Emoji analysis error: {e}")
        # Non-fatal — continue without emoji
        from services.emoji_analyzer import EmojiSentimentResult
        emoji_result = EmojiSentimentResult("neutral", 0.5, {}, [])

    # ── Step 5: Image Analysis ─────────────────────────────────────────────
    try:
        image_result = await analyze_image_sentiment(tweet.images)
        logger.info(f"[{analysis_id}] Image: {image_result.label} ({image_result.score:.3f})")
    except Exception as e:
        logger.error(f"[{analysis_id}] Image analysis error: {e}")
        from services.image_analyzer import ImageSentimentResult
        image_result = ImageSentimentResult(
            "neutral", 0.5,
            {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            analyzed=False, method="error"
        )

    # ── Step 6: Fusion ─────────────────────────────────────────────────────
    fusion = fuse_sentiments(text_result, emoji_result, image_result, tweet.emojis, language)
    logger.info(f"[{analysis_id}] Final: {fusion.final_sentiment} ({fusion.confidence:.3f})")

    # ── Step 7: Persist Result ─────────────────────────────────────────────
    elapsed_ms = int((time.time() - start_time) * 1000)

    full_result = {
        "tweet_data": {
            "id": tweet.id,
            "text": tweet.text,
            "author": tweet.author,
            "author_handle": tweet.author_handle,
            "timestamp": tweet.timestamp,
            "images": tweet.images,
            "emojis": tweet.emojis,
            "likes": tweet.likes,
            "retweets": tweet.retweets,
            "replies_count": tweet.replies_count,
            "url": tweet.url,
            "avatar": tweet.avatar,
            "verified": tweet.verified,
        },
        "sentiment": {
            "final": fusion.final_sentiment,
            "confidence": fusion.confidence,
            "label": fusion.label,
            "breakdown": fusion.breakdown,
        },
        "model_comparison": fusion.model_comparison,
        "sarcasm": fusion.sarcasm,
        "language": fusion.language,
        "fusion_weights": fusion.fusion_weights,
        "processing_time_ms": elapsed_ms,
    }

    try:
        record = AnalysisRecord(
            id=analysis_id,
            tweet_url=req.tweet_url,
            tweet_text=tweet.text,
            tweet_author=tweet.author_handle,
            tweet_timestamp=tweet.timestamp,
            final_sentiment=fusion.final_sentiment,
            confidence=fusion.confidence,
            text_sentiment=text_result.label,
            text_score=text_result.score,
            emoji_sentiment=emoji_result.label,
            emoji_score=emoji_result.score,
            image_sentiment=image_result.label,
            image_score=image_result.score,
            language=fusion.language,
            sarcasm_detected=fusion.sarcasm["detected"],
            sarcasm_score=fusion.sarcasm["score"],
            full_result=full_result,
        )
        db.add(record)
        await db.flush()
        logger.info(f"[{analysis_id}] Saved to DB")
    except Exception as e:
        logger.error(f"[{analysis_id}] DB save error (non-fatal): {e}")

    return AnalyzeResponse(
        analysis_id=analysis_id,
        **full_result,
    )
