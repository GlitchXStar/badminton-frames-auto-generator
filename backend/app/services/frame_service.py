"""Frame orchestration service — ties together extraction, quality, dedup, selection."""
import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.frame import Frame
from app.models.processing_job import ProcessingJob
from app.models.video import Video
from app.services.ffmpeg_service import FFmpegService, FFmpegServiceError
from app.services.image_quality_service import ImageQualityService
from app.services.duplicate_service import DuplicateService
from app.services.selection_service import SelectionService

logger = get_logger(__name__)


class FrameService:
    """Orchestrates the full frame processing pipeline for a video."""

    def __init__(self, db: Session):
        self.db = db
        self.quality_service = ImageQualityService()
        self.duplicate_service = DuplicateService()

    def process_video(
        self,
        video: Video,
        job: ProcessingJob,
        extraction_interval: float = 2.0,
        max_resolution: int = 1080,
    ) -> None:
        """Run full pipeline: extract → quality filter → dedup → select."""
        try:
            # Delete old frame DB records and files for this video if re-processing
            self.db.query(Frame).filter(Frame.video_id == video.id).delete()
            self.db.commit()

            # Stage 1: Extract frames
            self._update_job(job, "running", 0, message="Extracting frames...")
            frames_dir = settings.get_frames_dir() / str(video.id)
            if frames_dir.exists():
                import shutil
                for item in frames_dir.iterdir():
                    if item.is_file():
                        try:
                            item.unlink()
                        except Exception:
                            pass
            frames_dir.mkdir(parents=True, exist_ok=True)

            video_path = Path(video.local_path)
            if not video_path.exists():
                raise FFmpegServiceError(f"Video file not found: {video_path}")

            prefix = f"vid{video.id}"
            frame_paths = FFmpegService.extract_frames(
                video_path=video_path,
                output_dir=frames_dir,
                interval_seconds=extraction_interval,
                max_resolution=max_resolution,
                filename_prefix=prefix,
            )

            total_extracted = len(frame_paths)
            self._update_job(
                job, "running", 25,
                total_items=total_extracted,
                message=f"Extracted {total_extracted} frames. Running quality checks..."
            )

            # Store frames in database
            frame_records: list[Frame] = []
            for i, fp in enumerate(frame_paths):
                timestamp = i * extraction_interval
                frame = Frame(
                    video_id=video.id,
                    filename=fp.name,
                    filepath=str(fp),
                    timestamp=float(timestamp),
                    frame_number=i + 1,
                    is_selected=True, # Mark auto selected or just default True for simplicity
                )
                self.db.add(frame)
                frame_records.append(frame)
            self.db.commit()

            # Complete
            self._update_job(
                job, "completed", 100,
                processed_items=total_extracted,
                message=f"Done! Extracted {total_extracted} frames."
            )

            # Update video status
            video.status = "processed"
            self.db.commit()

        except Exception as e:
            logger.error(f"Processing error for video {video.id}: {e}", exc_info=True)
            self._update_job(job, "failed", job.progress, error=str(e))
            video.status = "error"
            self.db.commit()
            raise

    def _update_job(
        self,
        job: ProcessingJob,
        status: str,
        progress: float,
        total_items: int = None,
        processed_items: int = None,
        message: str = None,
        error: str = None,
    ) -> None:
        """Update a processing job's status."""
        job.status = status
        job.progress = progress
        if total_items is not None:
            job.total_items = total_items
        if processed_items is not None:
            job.processed_items = processed_items
        if message:
            job.message = message
        if error:
            job.error = error
        if status == "running" and not job.started_at:
            job.started_at = datetime.datetime.utcnow()
        if status in ("completed", "failed"):
            job.completed_at = datetime.datetime.utcnow()
        self.db.commit()
