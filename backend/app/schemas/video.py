"""Pydantic schemas for Video."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class VideoCreate(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL")
    extraction_interval: float = Field(2.0, description="Seconds between frame captures")
    max_resolution: int = Field(1080, description="Maximum resolution height")

    @field_validator("youtube_url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        """Validate that the URL looks like a YouTube URL."""
        patterns = [
            r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}",
            r"^https?://youtu\.be/[\w-]{11}",
            r"^https?://(www\.)?youtube\.com/shorts/[\w-]{11}",
        ]
        if not any(re.match(p, v) for p in patterns):
            raise ValueError(
                "Invalid YouTube URL. Expected format: "
                "https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID"
            )
        return v

    @field_validator("extraction_interval")
    @classmethod
    def validate_interval(cls, v: float) -> float:
        if v < 0.01 or v > 60.0:
            raise ValueError("Extraction interval must be between 0.01s and 60.0s")
        return v

    @field_validator("max_resolution")
    @classmethod
    def validate_resolution(cls, v: int) -> int:
        allowed = [720, 1080]
        if v not in allowed:
            raise ValueError(f"Max resolution must be one of {allowed}")
        return v


class VideoResponse(BaseModel):
    id: int
    project_id: int
    youtube_url: str
    youtube_id: Optional[str]
    title: Optional[str]
    duration: Optional[float]
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    extraction_interval: Optional[float] = 2.0
    max_resolution: Optional[int] = 1080
    local_path: Optional[str]
    status: str
    created_at: datetime
    frame_count: Optional[int] = 0

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    videos: list[VideoResponse]
    total: int
