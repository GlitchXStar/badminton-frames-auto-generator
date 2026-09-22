"""Video SQLAlchemy model."""
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    youtube_url = Column(String(500), nullable=False)
    youtube_id = Column(String(50), nullable=True)
    title = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    extraction_interval = Column(Float, nullable=True, default=2.0)
    max_resolution = Column(Integer, nullable=True, default=1080)
    local_path = Column(String(1000), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="videos")
    frames = relationship("Frame", back_populates="video", cascade="all, delete-orphan")
    processing_jobs = relationship(
        "ProcessingJob", back_populates="video", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_videos_project_id", "project_id"),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title='{self.title}')>"
