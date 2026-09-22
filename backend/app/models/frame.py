"""Frame SQLAlchemy model."""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Index, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Frame(Base):
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1000), nullable=False)
    timestamp = Column(Float, nullable=True)  # seconds into video
    frame_number = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    blur_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    sha256 = Column(String(64), nullable=True)
    phash = Column(String(64), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    is_rejected = Column(Boolean, default=False)
    is_selected = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    selection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="frames")

    __table_args__ = (
        Index("ix_frames_video_id", "video_id"),
        Index("ix_frames_sha256", "sha256"),
        Index("ix_frames_phash", "phash"),
        Index("ix_frames_is_selected", "is_selected"),
        Index("ix_frames_is_rejected", "is_rejected"),
    )

    def __repr__(self) -> str:
        return f"<Frame(id={self.id}, filename='{self.filename}')>"
