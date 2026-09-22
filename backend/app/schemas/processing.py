"""Pydantic schemas for Processing."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProcessingRequest(BaseModel):
    extraction_interval: float = Field(2.0, description="Seconds between frame captures")
    max_resolution: int = Field(1080, description="Maximum resolution height")


class JobResponse(BaseModel):
    id: int
    project_id: int
    video_id: Optional[int]
    job_type: str
    status: str
    progress: float
    total_items: int
    processed_items: int
    message: Optional[str]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    batch_name: Optional[str] = Field(None, description="Custom batch name prefix")
    max_images: Optional[int] = Field(None, description="Limit export to N images")


class ExportResponse(BaseModel):
    export_id: str
    filename: str
    image_count: int
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    ffmpeg: str
    ytdlp: str
    data_dir: str
