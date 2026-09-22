"""Processing API routes — download, extract, filter, select pipeline."""
import threading
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.core.logging import get_logger
from app.models.video import Video
from app.models.processing_job import ProcessingJob
from app.schemas.processing import ProcessingRequest, JobResponse
from app.services.youtube_service import YouTubeService, YouTubeServiceError
from app.services.frame_service import FrameService

logger = get_logger(__name__)

router = APIRouter(tags=["processing"])


def _run_pipeline(video_id: int, job_id: int, extraction_interval: float, max_resolution: int):
    """Background thread function for running the processing pipeline."""
    db = SessionLocal()
    try:
        video = db.get(Video, video_id)
        job = db.get(ProcessingJob, job_id)
        if not video or not job:
            logger.error(f"Video {video_id} or Job {job_id} not found")
            return

        # Step 1: Download video if needed
        if not video.local_path or not __import__("pathlib").Path(video.local_path).exists():
            job.status = "running"
            job.progress = 5.0
            job.message = "Downloading video..."
            db.commit()

            video_dir = settings.get_videos_dir() / str(video.project_id)
            try:
                local_path = YouTubeService.download_video(
                    url=video.youtube_url,
                    output_dir=video_dir,
                    max_resolution=max_resolution,
                    filename_prefix=f"video_{video.id}",
                )
                video.local_path = str(local_path)
                video.status = "downloaded"
                db.commit()
            except YouTubeServiceError as e:
                job.status = "failed"
                job.error = str(e)
                job.message = f"Download failed: {e}"
                video.status = "error"
                db.commit()
                return

        # Step 2: Run frame service pipeline
        frame_service = FrameService(db)
        frame_service.process_video(
            video=video,
            job=job,
            extraction_interval=extraction_interval,
            max_resolution=max_resolution,
        )

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        try:
            job = db.get(ProcessingJob, job_id)
            if job:
                job.status = "failed"
                job.error = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


@router.post("/api/videos/{video_id}/process", response_model=JobResponse, status_code=202)
def process_video(video_id: int, data: ProcessingRequest = None, db: Session = Depends(get_db)):
    """Start processing a video (download → extract → filter → select)."""
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check if already processing
    active_job = (
        db.query(ProcessingJob)
        .filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.status.in_(["pending", "running"]),
        )
        .first()
    )
    if active_job:
        raise HTTPException(status_code=409, detail="Video is already being processed")

    # Determine interval and resolution from payload or video defaults
    interval = (data.extraction_interval if data and data.extraction_interval is not None 
                else getattr(video, "extraction_interval", None) or 2.0)
    max_res = (data.max_resolution if data and data.max_resolution is not None 
               else getattr(video, "max_resolution", None) or 1080)

    # Save used values on video
    video.extraction_interval = interval
    video.max_resolution = max_res
    db.commit()

    # Create job
    job = ProcessingJob(
        project_id=video.project_id,
        video_id=video.id,
        job_type="full_pipeline",
        status="pending",
        message="Queued for processing...",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Run pipeline in background thread
    thread = threading.Thread(
        target=_run_pipeline,
        args=(video.id, job.id, interval, max_res),
        daemon=True,
    )
    thread.start()

    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        video_id=job.video_id,
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        total_items=job.total_items,
        processed_items=job.processed_items,
        message=job.message,
        error=job.error,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


@router.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get processing job status."""
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        video_id=job.video_id,
        job_type=job.job_type,
        status=job.status,
        progress=job.progress,
        total_items=job.total_items,
        processed_items=job.processed_items,
        message=job.message,
        error=job.error,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )
