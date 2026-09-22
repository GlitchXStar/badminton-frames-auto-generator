"""Export service for creating CVAT-ready ZIP batches."""
import csv
import io
import json
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.frame import Frame
from app.models.project import Project
from app.models.video import Video

logger = get_logger(__name__)


class ExportServiceError(Exception):
    """Raised when an export operation fails."""
    pass


class ExportService:
    """Service for exporting selected frames as CVAT-ready ZIP batches."""

    def __init__(self, db: Session):
        self.db = db

    def export_project(
        self,
        project: Project,
        batch_name: Optional[str] = None,
        max_images: Optional[int] = None,
    ) -> dict:
        """Export selected frames from a project as a ZIP file.

        Returns dict with export_id, filename, path, image_count.
        """
        # Get selected frames
        selected_frames = (
            self.db.query(Frame)
            .join(Video)
            .filter(
                Video.project_id == project.id,
                Frame.is_selected == True,
            )
            .order_by(Frame.quality_score.desc())
            .all()
        )

        if not selected_frames:
            raise ExportServiceError("No selected frames to export")

        # Limit if max_images specified
        if max_images and len(selected_frames) > max_images:
            selected_frames = selected_frames[:max_images]

        # Generate export identifiers
        export_id = uuid.uuid4().hex[:12]
        prefix = batch_name or project.name.replace(" ", "_")
        safe_prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")
        filename = f"{safe_prefix}_CVAT_Batch_{export_id[:6]}.zip"

        exports_dir = settings.get_exports_dir()
        exports_dir.mkdir(parents=True, exist_ok=True)
        zip_path = exports_dir / filename

        # Build the ZIP
        logger.info(f"Creating export ZIP: {filename} with {len(selected_frames)} images")

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add images with sequential naming
                manifest_rows = []
                for i, frame in enumerate(selected_frames, 1):
                    seq_name = f"{safe_prefix}_{i:06d}.jpg"
                    src_path = Path(frame.filepath)

                    if not src_path.exists():
                        logger.warning(f"Frame file missing: {src_path}")
                        continue

                    zf.write(src_path, f"images/{seq_name}")

                    # Get source video info
                    video = frame.video
                    manifest_rows.append({
                        "filename": seq_name,
                        "source_video_id": video.id if video else "",
                        "youtube_url": video.youtube_url if video else "",
                        "timestamp": frame.timestamp or "",
                        "frame_number": frame.frame_number or "",
                        "width": frame.width or "",
                        "height": frame.height or "",
                        "blur_score": round(frame.blur_score, 2) if frame.blur_score else "",
                        "quality_score": round(frame.quality_score, 2) if frame.quality_score else "",
                        "sha256": frame.sha256 or "",
                        "phash": frame.phash or "",
                    })

                # Add source_manifest.csv
                csv_buffer = io.StringIO()
                if manifest_rows:
                    writer = csv.DictWriter(csv_buffer, fieldnames=manifest_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(manifest_rows)
                zf.writestr("metadata/source_manifest.csv", csv_buffer.getvalue())

                # Add dataset_report.json
                report = self._generate_report(project, selected_frames)
                zf.writestr(
                    "metadata/dataset_report.json",
                    json.dumps(report, indent=2, default=str),
                )

                # Add README.txt
                readme = self._generate_readme(project, len(manifest_rows), export_id)
                zf.writestr("README.txt", readme)

            logger.info(f"Export complete: {zip_path}")

            return {
                "export_id": export_id,
                "filename": filename,
                "path": str(zip_path),
                "image_count": len(manifest_rows),
            }

        except Exception as e:
            # Clean up partial ZIP
            if zip_path.exists():
                zip_path.unlink()
            raise ExportServiceError(f"Export failed: {e}")

    def _generate_report(self, project: Project, selected_frames: list[Frame]) -> dict:
        """Generate dataset_report.json content."""
        # Count stats
        all_frames = (
            self.db.query(Frame)
            .join(Video)
            .filter(Video.project_id == project.id)
            .all()
        )
        videos = self.db.query(Video).filter(Video.project_id == project.id).all()

        quality_scores = [f.quality_score for f in selected_frames if f.quality_score]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Resolution distribution
        res_dist: dict[str, int] = {}
        for f in selected_frames:
            if f.width and f.height:
                key = f"{f.width}x{f.height}"
                res_dist[key] = res_dist.get(key, 0) + 1

        return {
            "project": project.name,
            "export_date": datetime.utcnow().isoformat(),
            "target_count": project.target_images,
            "actual_count": len(selected_frames),
            "source_videos": len(videos),
            "frames_extracted": len(all_frames),
            "duplicates_removed": sum(1 for f in all_frames if f.is_duplicate),
            "rejected": sum(1 for f in all_frames if f.is_rejected),
            "selected": len(selected_frames),
            "average_quality": round(avg_quality, 2),
            "resolution_distribution": res_dist,
        }

    def _generate_readme(self, project: Project, image_count: int, export_id: str) -> str:
        """Generate README.txt content for the export."""
        return f"""BADMINTON DATASET GENERATOR — Export Batch
============================================

Dataset generated by Badminton Dataset Generator.

These images are intentionally UNANNOTATED.

Next step:
  Import these images into CVAT and manually annotate Shoes
  using oriented bounding boxes (OBB).

Project Details:
  Project ID:      {project.id}
  Batch Name:      {project.name}
  Image Count:     {image_count}
  Target Count:    {project.target_images}
  Generation Date: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
  Export ID:       {export_id}

Contents:
  images/          — Unannotated badminton court images (JPEG)
  metadata/        — Source manifest and dataset report
    source_manifest.csv   — Per-image metadata
    dataset_report.json   — Aggregate statistics

CVAT Import Instructions:
  1. Create a new CVAT task
  2. Upload the images from the images/ folder
  3. Define annotation labels (e.g., "Shoe" with OBB)
  4. Assign annotators
  5. Begin manual annotation
"""
