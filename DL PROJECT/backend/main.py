"""
Main FastAPI Application Entrypoint.
Abstractive Text Summarization using Hugging Face Transformers.
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from backend.api.routes import router as api_router
from services.model_manager import ModelManager

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("neural_summarizer")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Neural Summarizer Backend...")
    # Pre-detect device without loading bulky model at boot to keep startup fast
    manager = ModelManager()
    logger.info(f"Target execution device: {manager.device_name}")
    yield
    logger.info("Shutting down Neural Summarizer Backend...")
    manager.unload()

app = FastAPI(
    title=config.PROJECT_TITLE,
    description="Production-grade REST API for Abstractive Text Summarization using Seq2Seq Transformers (BART & T5).",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Neural Summarizer API",
        "title": config.PROJECT_TITLE,
        "team_lead": config.TEAM_LEAD,
        "docs": "/docs",
        "health": "/api/health",
        "models": "/api/models"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
