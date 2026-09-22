"""Pydantic schemas for Frame."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FrameUpdate(BaseModel):
    is_selected: Optional[bool] = None
    is_rejected: Optional[bool] = None
    rejection_reason: Optional[str] = None


class BulkFrameAction(BaseModel):
    frame_ids: list[int] = Field(..., min_length=1)
    action: str = Field(..., description="select, reject, or reset")
    rejection_reason: Optional[str] = None


class FrameResponse(BaseModel):
    id: int
    video_id: int
    filename: str
    filepath: str
    timestamp: Optional[float]
    frame_number: Optional[int]
    width: Optional[int]
    height: Optional[int]
    blur_score: Optional[float]
    quality_score: Optional[float]
    sha256: Optional[str]
    phash: Optional[str]
    is_duplicate: bool
    is_rejected: bool
    is_selected: bool
    rejection_reason: Optional[str]
    selection_reason: Optional[str]
    created_at: datetime
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class FrameListResponse(BaseModel):
    frames: list[FrameResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FrameFilterParams(BaseModel):
    status: Optional[str] = None  # all, selected, rejected, duplicate, candidate
    video_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)
    sort_by: str = Field("timestamp", description="Sort field")
    sort_order: str = Field("asc", description="Sort order: asc or desc")
