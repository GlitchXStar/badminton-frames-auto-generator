"""Frame API routes — gallery, filtering, bulk operations."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

from app.core.database import get_db
from app.models.frame import Frame
from app.models.video import Video
from app.schemas.frame import (
    FrameUpdate,
    BulkFrameAction,
    FrameResponse,
    FrameListResponse,
)

router = APIRouter(tags=["frames"])


def _frame_to_response(frame: Frame) -> FrameResponse:
    """Convert a Frame model to a FrameResponse."""
    return FrameResponse(
        id=frame.id,
        video_id=frame.video_id,
        filename=frame.filename,
        filepath=frame.filepath,
        timestamp=frame.timestamp,
        frame_number=frame.frame_number,
        width=frame.width,
        height=frame.height,
        blur_score=frame.blur_score,
        quality_score=frame.quality_score,
        sha256=frame.sha256,
        phash=frame.phash,
        is_duplicate=frame.is_duplicate,
        is_rejected=frame.is_rejected,
        is_selected=frame.is_selected,
        rejection_reason=frame.rejection_reason,
        selection_reason=frame.selection_reason,
        created_at=frame.created_at,
        image_url=f"/api/frames/{frame.id}/image",
    )


@router.get("/api/projects/{project_id}/frames", response_model=FrameListResponse)
def list_frames(
    project_id: int,
    status: str = Query(None, description="Filter: all, selected, rejected, duplicate, candidate"),
    video_id: int = Query(None, description="Filter by video ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10000, ge=1, le=10000),
    sort_by: str = Query("timestamp", description="Sort field"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db),
):
    """List frames for a project with filtering and pagination."""
    query = (
        db.query(Frame)
        .join(Video)
        .filter(Video.project_id == project_id)
    )

    # Apply filters
    if video_id:
        query = query.filter(Frame.video_id == video_id)

    if status == "selected":
        query = query.filter(Frame.is_selected == True)
    elif status == "rejected":
        query = query.filter(Frame.is_rejected == True)
    elif status == "duplicate":
        query = query.filter(Frame.is_duplicate == True)
    elif status == "candidate":
        query = query.filter(
            Frame.is_rejected == False,
            Frame.is_duplicate == False,
        )

    # Count total
    total = query.count()

    # Apply sorting
    sort_column = getattr(Frame, sort_by, Frame.timestamp)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    frames = query.offset(offset).limit(page_size).all()

    return FrameListResponse(
        frames=[_frame_to_response(f) for f in frames],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.patch("/api/frames/{frame_id}", response_model=FrameResponse)
def update_frame(frame_id: int, data: FrameUpdate, db: Session = Depends(get_db)):
    """Update a single frame's selection/rejection status."""
    frame = db.get(Frame, frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    if data.is_selected is not None:
        frame.is_selected = data.is_selected
        if data.is_selected:
            frame.is_rejected = False
            frame.rejection_reason = None
            frame.selection_reason = "Manual selection"

    if data.is_rejected is not None:
        frame.is_rejected = data.is_rejected
        if data.is_rejected:
            frame.is_selected = False
            frame.selection_reason = None
            frame.rejection_reason = data.rejection_reason or "Manual rejection"

    if data.is_selected is False and data.is_rejected is False:
        # Reset
        frame.selection_reason = None
        frame.rejection_reason = None

    db.commit()
    db.refresh(frame)
    return _frame_to_response(frame)


@router.post("/api/projects/{project_id}/frames/bulk")
def bulk_frame_action(project_id: int, data: BulkFrameAction, db: Session = Depends(get_db)):
    """Perform bulk action on frames."""
    frames = (
        db.query(Frame)
        .join(Video)
        .filter(
            Video.project_id == project_id,
            Frame.id.in_(data.frame_ids),
        )
        .all()
    )

    if not frames:
        raise HTTPException(status_code=404, detail="No matching frames found")

    updated = 0
    for frame in frames:
        if data.action == "select":
            frame.is_selected = True
            frame.is_rejected = False
            frame.rejection_reason = None
            frame.selection_reason = "Bulk selection"
        elif data.action == "reject":
            frame.is_selected = False
            frame.is_rejected = True
            frame.selection_reason = None
            frame.rejection_reason = data.rejection_reason or "Bulk rejection"
        elif data.action == "reset":
            frame.is_selected = False
            frame.is_rejected = False
            frame.selection_reason = None
            frame.rejection_reason = None
        updated += 1

    db.commit()
    return {"updated": updated, "action": data.action}


@router.get("/api/frames/{frame_id}/image")
def get_frame_image(frame_id: int, db: Session = Depends(get_db)):
    """Serve a frame image file."""
    from fastapi.responses import FileResponse
    from pathlib import Path

    frame = db.get(Frame, frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")

    filepath = Path(frame.filepath)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Frame image file not found")

    return FileResponse(
        path=str(filepath),
        media_type="image/jpeg",
        filename=frame.filename,
    )
