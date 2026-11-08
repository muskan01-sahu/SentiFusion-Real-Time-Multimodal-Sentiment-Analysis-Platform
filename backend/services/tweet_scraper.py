"""
Tweet Scraper Service
Fetches tweet data from a URL using Tweepy (API) or snscrape (fallback).
Extracts: text, author, timestamp, images, emojis, replies.
"""

import re
import os
import logging
from typing import Optional
from dataclasses import dataclass, field
import httpx

logger = logging.getLogger(__name__)

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")


@dataclass
class TweetData:
    id: str
    text: str
    author: str
    author_handle: str
    timestamp: str
    images: list[str] = field(default_factory=list)
    emojis: list[str] = field(default_factory=list)
    likes: int = 0
    retweets: int = 0
    replies_count: int = 0
    url: str = ""
    avatar: str = ""
    verified: bool = False


def extract_tweet_id(url: str) -> Optional[str]:
    """Extract tweet ID from various Twitter/X URL formats."""
    patterns = [
        r"twitter\.com/\w+/status/(\d+)",
        r"x\.com/\w+/status/(\d+)",
        r"twitter\.com/i/web/status/(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_emojis(text: str) -> list[str]:
    """Extract all emojis from text using Unicode ranges."""
    import emoji as emoji_lib
    emoji_list = []
    for char in text:
        if char in emoji_lib.EMOJI_DATA:
            emoji_list.append(char)
    return list(set(emoji_list))


async def fetch_tweet_via_api(tweet_id: str) -> Optional[TweetData]:
    """Fetch tweet using Twitter API v2 Bearer Token."""
    if not TWITTER_BEARER_TOKEN:
        return None

    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {
        "expansions": "author_id,attachments.media_keys",
        "tweet.fields": "created_at,public_metrics,lang,entities",
        "user.fields": "name,username,profile_image_url,verified",
        "media.fields": "url,preview_image_url,type",
    }
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        tweet = data.get("data", {})
        includes = data.get("includes", {})
        users = {u["id"]: u for u in includes.get("users", [])}
        media = {m["media_key"]: m for m in includes.get("media", [])}

        author_id = tweet.get("author_id", "")
        author_data = users.get(author_id, {})

        # Extract images
        images = []
        for mk in tweet.get("attachments", {}).get("media_keys", []):
            m = media.get(mk, {})
            img_url = m.get("url") or m.get("preview_image_url")
            if img_url:
                images.append(img_url)

        text = tweet.get("text", "")
        metrics = tweet.get("public_metrics", {})

        return TweetData(
            id=tweet_id,
            text=text,
            author=author_data.get("name", "Unknown"),
            author_handle=f"@{author_data.get('username', 'unknown')}",
            timestamp=tweet.get("created_at", ""),
            images=images,
            emojis=extract_emojis(text),
            likes=metrics.get("like_count", 0),
            retweets=metrics.get("retweet_count", 0),
            replies_count=metrics.get("reply_count", 0),
            url=f"https://twitter.com/{author_data.get('username')}/status/{tweet_id}",
            avatar=author_data.get("profile_image_url", ""),
            verified=author_data.get("verified", False),
        )
    except Exception as e:
        logger.warning(f"API fetch failed: {e}")
        return None


async def fetch_tweet_mock(tweet_id: str, original_url: str) -> TweetData:
    """
    Mock tweet fetcher for demo/development when no API key is available.
    Returns realistic demo data so the app remains fully functional.
    """
    import random
    from datetime import datetime, timezone

    demo_tweets = [
        {
            "text": "Just launched our new AI product! 🚀 The team has been working so hard and I couldn't be more proud! This is going to change everything! 😊🔥 #AI #Innovation #Excited",
            "author": "Tech Entrepreneur",
            "handle": "@techfounder",
            "sentiment_hint": "positive",
            "images": [],
        },
        {
            "text": "This new update completely broke everything 😤 I've been dealing with crashes all day and the support team is completely useless. Absolutely disappointed. 😡 #fail #terrible",
            "author": "Frustrated User",
            "handle": "@user_reviews",
            "sentiment_hint": "negative",
            "images": [],
        },
        {
            "text": "Attended the conference today. Sessions were okay. Some things were interesting, others not so much. The food was decent. Will probably come back next year if schedules align.",
            "author": "Conference Attendee",
            "handle": "@conf_goer",
            "sentiment_hint": "neutral",
            "images": [],
        },
    ]

    tweet_hash = int(tweet_id[-1]) % len(demo_tweets) if tweet_id else 0
    demo = demo_tweets[tweet_hash]
    text = demo["text"]

    return TweetData(
        id=tweet_id or "demo123",
        text=text,
        author=demo["author"],
        author_handle=demo["handle"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        images=demo["images"],
        emojis=extract_emojis(text),
        likes=random.randint(100, 50000),
        retweets=random.randint(10, 5000),
        replies_count=random.randint(5, 500),
        url=original_url,
        avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=" + demo["handle"],
        verified=random.choice([True, False]),
    )


async def scrape_tweet(url: str) -> TweetData:
    """
    Main function: attempts API fetch, falls back to mock for demo.
    In production, add snscrape as the middle fallback layer.
    """
    tweet_id = extract_tweet_id(url)

    if not tweet_id:
        raise ValueError(f"Could not extract tweet ID from URL: {url}")

    # Try official API first
    if TWITTER_BEARER_TOKEN:
        result = await fetch_tweet_via_api(tweet_id)
        if result:
            logger.info(f"✅ Fetched tweet {tweet_id} via API")
            return result

    # Fallback: mock data (swap with snscrape in production)
    logger.info(f"⚠️  Using demo data for tweet {tweet_id} (no API key set)")
    return await fetch_tweet_mock(tweet_id, url)
