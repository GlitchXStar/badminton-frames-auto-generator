"""Application configuration using Pydantic Settings."""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Badminton Dataset Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///data/badminton_dataset.db"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Data directories (relative to project root)
    DATA_DIR: str = "data"
    VIDEOS_DIR: str = "data/videos"
    FRAMES_DIR: str = "data/frames"
    SELECTED_DIR: str = "data/selected"
    REJECTED_DIR: str = "data/rejected"
    EXPORTS_DIR: str = "data/exports"
    PROJECTS_DIR: str = "data/projects"

    # Video processing defaults
    DEFAULT_EXTRACTION_INTERVAL: int = 2  # seconds
    DEFAULT_MAX_RESOLUTION: int = 1080  # pixels height
    JPEG_QUALITY: int = 95

    # Image quality thresholds
    MIN_RESOLUTION_WIDTH: int = 640
    MIN_RESOLUTION_HEIGHT: int = 360
    BLUR_THRESHOLD: float = 100.0  # Laplacian variance below this = blurry
    BLACK_FRAME_THRESHOLD: float = 10.0  # Mean pixel value below this = black

    # Duplicate detection
    PHASH_SIMILARITY_THRESHOLD: int = 8  # Hamming distance threshold

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_base_dir(self) -> Path:
        """Get the base directory for the application (project root)."""
        return Path(__file__).resolve().parent.parent.parent.parent

    def get_data_dir(self) -> Path:
        return self.get_base_dir() / self.DATA_DIR

    def get_videos_dir(self) -> Path:
        return self.get_base_dir() / self.VIDEOS_DIR

    def get_frames_dir(self) -> Path:
        return self.get_base_dir() / self.FRAMES_DIR

    def get_selected_dir(self) -> Path:
        return self.get_base_dir() / self.SELECTED_DIR

    def get_rejected_dir(self) -> Path:
        return self.get_base_dir() / self.REJECTED_DIR

    def get_exports_dir(self) -> Path:
        return self.get_base_dir() / self.EXPORTS_DIR

    def get_projects_dir(self) -> Path:
        return self.get_base_dir() / self.PROJECTS_DIR

    def ensure_directories(self) -> None:
        """Create all required data directories if they don't exist."""
        for dir_path in [
            self.get_data_dir(),
            self.get_videos_dir(),
            self.get_frames_dir(),
            self.get_selected_dir(),
            self.get_rejected_dir(),
            self.get_exports_dir(),
            self.get_projects_dir(),
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
