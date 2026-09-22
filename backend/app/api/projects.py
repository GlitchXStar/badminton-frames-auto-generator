"""Project API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.project import Project
from app.models.video import Video
from app.models.frame import Frame
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStats,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _get_project_stats(db: Session, project_id: int) -> ProjectStats:
    """Compute statistics for a project."""
    video_count = db.query(func.count(Video.id)).filter(Video.project_id == project_id).scalar() or 0

    # Individual count queries for SQLite compatibility
    total_frames = (
        db.query(func.count(Frame.id))
        .join(Video)
        .filter(Video.project_id == project_id)
        .scalar() or 0
    )
    selected = (
        db.query(func.count(Frame.id))
        .join(Video)
        .filter(Video.project_id == project_id, Frame.is_selected == True)
        .scalar() or 0
    )
    rejected = (
        db.query(func.count(Frame.id))
        .join(Video)
        .filter(Video.project_id == project_id, Frame.is_rejected == True)
        .scalar() or 0
    )
    duplicates = (
        db.query(func.count(Frame.id))
        .join(Video)
        .filter(Video.project_id == project_id, Frame.is_duplicate == True)
        .scalar() or 0
    )
    candidates = total_frames - rejected - duplicates

    return ProjectStats(
        total_videos=video_count,
        total_frames=total_frames,
        candidates=candidates,
        duplicates=duplicates,
        rejected=rejected,
        selected=selected,
    )


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    # Check for duplicate name
    existing = db.query(Project).filter(Project.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Project '{data.name}' already exists")

    project = Project(
        name=data.name,
        description=data.description,
        target_images=data.target_images,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    stats = _get_project_stats(db, project.id)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_images=project.target_images,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )


@router.get("", response_model=ProjectListResponse)
def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    result = []
    for p in projects:
        stats = _get_project_stats(db, p.id)
        result.append(
            ProjectResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                target_images=p.target_images,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
                stats=stats,
            )
        )
    return ProjectListResponse(projects=result, total=len(result))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = _get_project_stats(db, project.id)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        target_images=project.target_images,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        stats=stats,
    )
