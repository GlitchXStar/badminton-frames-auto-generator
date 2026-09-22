"""ProcessingJob SQLAlchemy model."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True)
    job_type = Column(String(50), nullable=False)  # download, extract, quality, duplicate, select
    status = Column(String(50), nullable=False, default="pending")
    progress = Column(Float, default=0.0)
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="processing_jobs")
    video = relationship("Video", back_populates="processing_jobs")

    __table_args__ = (
        Index("ix_processing_jobs_project_id", "project_id"),
        Index("ix_processing_jobs_video_id", "video_id"),
    )

    def __repr__(self) -> str:
        return f"<ProcessingJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"
