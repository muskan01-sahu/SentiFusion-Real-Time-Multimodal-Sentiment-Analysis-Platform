"""
Database Models — SQLAlchemy + SQLite
Stores analysis history for the History panel feature.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, JSON, Boolean
from datetime import datetime, timezone
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./sentiment_history.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tweet_url: Mapped[str] = mapped_column(String, nullable=False)
    tweet_text: Mapped[str] = mapped_column(String, nullable=True)
    tweet_author: Mapped[str] = mapped_column(String, nullable=True)
    tweet_timestamp: Mapped[str] = mapped_column(String, nullable=True)

    # Sentiment results
    final_sentiment: Mapped[str] = mapped_column(String, nullable=False)  # positive/negative/neutral
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Breakdown scores
    text_sentiment: Mapped[str] = mapped_column(String, nullable=True)
    text_score: Mapped[float] = mapped_column(Float, nullable=True)
    emoji_sentiment: Mapped[str] = mapped_column(String, nullable=True)
    emoji_score: Mapped[float] = mapped_column(Float, nullable=True)
    image_sentiment: Mapped[str] = mapped_column(String, nullable=True)
    image_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Additional
    language: Mapped[str] = mapped_column(String, nullable=True, default="en")
    sarcasm_detected: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    sarcasm_score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

    # Full JSON result blob
    full_result: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
