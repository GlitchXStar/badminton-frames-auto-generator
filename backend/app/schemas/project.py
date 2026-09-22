"""Pydantic schemas for Project."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000)
    target_images: int = Field(500, ge=1, le=10000, description="Target number of images")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_images: Optional[int] = Field(None, ge=1, le=10000)
    status: Optional[str] = None


class ProjectStats(BaseModel):
    total_videos: int = 0
    total_frames: int = 0
    candidates: int = 0
    duplicates: int = 0
    rejected: int = 0
    selected: int = 0


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    target_images: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    stats: Optional[ProjectStats] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
