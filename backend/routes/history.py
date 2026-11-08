"""
/api/history — Analysis History Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.database import get_db, AnalysisRecord

router = APIRouter()


@router.get("/history")
async def get_history(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get paginated analysis history."""
    stmt = (
        select(AnalysisRecord)
        .order_by(desc(AnalysisRecord.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return {
        "total": len(records),
        "items": [
            {
                "id": r.id,
                "tweet_url": r.tweet_url,
                "tweet_text": r.tweet_text[:100] + "..." if r.tweet_text and len(r.tweet_text) > 100 else r.tweet_text,
                "tweet_author": r.tweet_author,
                "final_sentiment": r.final_sentiment,
                "confidence": r.confidence,
                "language": r.language,
                "sarcasm_detected": r.sarcasm_detected,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
    }


@router.get("/history/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get full analysis result by ID."""
    result = await db.get(AnalysisRecord, analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result.full_result


@router.delete("/history/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific analysis record."""
    record = await db.get(AnalysisRecord, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    await db.delete(record)
    return {"deleted": True, "id": analysis_id}
