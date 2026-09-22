"""Export API routes."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.models.project import Project
from app.schemas.processing import ExportRequest, ExportResponse
from app.services.export_service import ExportService, ExportServiceError

router = APIRouter(tags=["exports"])


@router.post("/api/projects/{project_id}/export", response_model=ExportResponse)
def export_project(
    project_id: int,
    data: ExportRequest = None,
    db: Session = Depends(get_db),
):
    """Export selected frames as a CVAT-ready ZIP batch."""
    if data is None:
        data = ExportRequest()

    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        service = ExportService(db)
        result = service.export_project(
            project=project,
            batch_name=data.batch_name,
            max_images=data.max_images,
        )
        return ExportResponse(
            export_id=result["export_id"],
            filename=result["filename"],
            image_count=result["image_count"],
            status="completed",
            message=f"Export ready: {result['filename']} ({result['image_count']} images)",
        )
    except ExportServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/exports/{export_id}/download")
def download_export(export_id: str, db: Session = Depends(get_db)):
    """Download an export ZIP file."""
    exports_dir = settings.get_exports_dir()

    # Find the export file by export_id in filename
    matches = list(exports_dir.glob(f"*{export_id[:6]}*.zip"))
    if not matches:
        raise HTTPException(status_code=404, detail="Export file not found")

    zip_path = matches[0]
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Export file has been deleted")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_path.name,
    )
