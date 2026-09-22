"""Video API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import get_db
from app.models.project import Project
from app.models.video import Video
from app.models.frame import Frame
from app.schemas.video import VideoCreate, VideoResponse, VideoListResponse
from app.services.youtube_service import YouTubeService, YouTubeServiceError

router = APIRouter(tags=["videos"])


@router.post("/api/projects/{project_id}/videos", response_model=VideoResponse, status_code=201)
def add_video(project_id: int, data: VideoCreate, db: Session = Depends(get_db)):
    """Add a YouTube video to a project."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Extract video ID
    video_id_str = YouTubeService.extract_video_id(data.youtube_url)
    if not video_id_str:
        raise HTTPException(status_code=400, detail="Could not extract YouTube video ID")

    # Check for duplicate video in project
    existing = (
        db.query(Video)
        .filter(Video.project_id == project_id, Video.youtube_id == video_id_str)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Video '{video_id_str}' already added to this project"
        )

    # Fetch metadata
    try:
        metadata = YouTubeService.get_metadata(data.youtube_url)
    except YouTubeServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

    video = Video(
        project_id=project_id,
        youtube_url=data.youtube_url,
        youtube_id=video_id_str,
        title=metadata.get("title", "Unknown"),
        duration=metadata.get("duration", 0),
        width=metadata.get("width", 0),
        height=metadata.get("height", 0),
        fps=metadata.get("fps", 0),
        extraction_interval=data.extraction_interval,
        max_resolution=data.max_resolution,
        status="metadata_fetched",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    frame_count = db.query(func.count(Frame.id)).filter(Frame.video_id == video.id).scalar() or 0

    return VideoResponse(
        id=video.id,
        project_id=video.project_id,
        youtube_url=video.youtube_url,
        youtube_id=video.youtube_id,
        title=video.title,
        duration=video.duration,
        width=video.width,
        height=video.height,
        fps=video.fps,
        extraction_interval=video.extraction_interval,
        max_resolution=video.max_resolution,
        local_path=video.local_path,
        status=video.status,
        created_at=video.created_at,
        frame_count=frame_count,
    )


@router.get("/api/projects/{project_id}/videos", response_model=VideoListResponse)
def list_videos(project_id: int, db: Session = Depends(get_db)):
    """List all videos in a project."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    videos = (
        db.query(Video)
        .filter(Video.project_id == project_id)
        .order_by(Video.created_at.desc())
        .all()
    )

    result = []
    for v in videos:
        frame_count = db.query(func.count(Frame.id)).filter(Frame.video_id == v.id).scalar() or 0
        result.append(
            VideoResponse(
                id=v.id,
                project_id=v.project_id,
                youtube_url=v.youtube_url,
                youtube_id=v.youtube_id,
                title=v.title,
                duration=v.duration,
                width=v.width,
                height=v.height,
                fps=v.fps,
                extraction_interval=v.extraction_interval,
                max_resolution=v.max_resolution,
                local_path=v.local_path,
                status=v.status,
                created_at=v.created_at,
                frame_count=frame_count,
            )
        )

    return VideoListResponse(videos=result, total=len(result))
