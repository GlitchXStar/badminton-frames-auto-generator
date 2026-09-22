"""FastAPI application — Badminton Dataset Generator."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging, get_logger
from app.schemas.processing import HealthResponse
from app.services.youtube_service import YouTubeService
from app.services.ffmpeg_service import FFmpegService

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging("DEBUG" if settings.DEBUG else "INFO")
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Ensure data directories exist
    settings.ensure_directories()
    logger.info(f"Data directory: {settings.get_data_dir()}")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Check dependencies
    if FFmpegService.check_available():
        logger.info(f"FFmpeg: {FFmpegService.get_version()}")
    else:
        logger.warning("FFmpeg is NOT available — video processing will fail")

    if YouTubeService.check_available():
        logger.info(f"yt-dlp: {YouTubeService.get_version()}")
    else:
        logger.warning("yt-dlp is NOT available — YouTube downloads will fail")

    yield

    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Collect and curate badminton footage frames for CVAT annotation",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api.projects import router as projects_router
from app.api.videos import router as videos_router
from app.api.processing import router as processing_router
from app.api.frames import router as frames_router
from app.api.exports import router as exports_router

app.include_router(projects_router)
app.include_router(videos_router)
app.include_router(processing_router)
app.include_router(frames_router)
app.include_router(exports_router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
def health_check():
    """Health check endpoint."""
    ffmpeg_status = "available"
    ffmpeg_version = FFmpegService.get_version()
    if not ffmpeg_version:
        ffmpeg_status = "not_installed"
        ffmpeg_version = "N/A"

    ytdlp_status = "available"
    ytdlp_version = YouTubeService.get_version()
    if not ytdlp_version:
        ytdlp_status = "not_installed"
        ytdlp_version = "N/A"

    data_dir = settings.get_data_dir()

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        database="connected",
        ffmpeg=f"{ffmpeg_status} ({ffmpeg_version})",
        ytdlp=f"{ytdlp_status} ({ytdlp_version})",
        data_dir=str(data_dir),
    )
