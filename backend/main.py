"""
Real-Time Multimodal Sentiment Analysis API
FastAPI Backend — Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routes.analyze import router as analyze_router
from routes.history import router as history_router
from models.database import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Multimodal Sentiment Analysis API...")
    await create_tables()
    logger.info("✅ Database tables initialized")
    yield
    logger.info("🛑 Shutting down API...")


app = FastAPI(
    title="Multimodal Sentiment Analysis API",
    description="""
    ## Real-Time Multimodal Sentiment Analysis of Twitter Posts
    
    Analyzes tweets using:
    - **RoBERTa** for text sentiment
    - **Emoji2Vec** for emoji sentiment  
    - **ViT** for image sentiment
    - **Fusion Layer** for final prediction
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(history_router, prefix="/api", tags=["History"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🧠 Multimodal Sentiment Analysis API",
        "docs": "/docs",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "models_loaded": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
