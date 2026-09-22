"""YouTube download service using yt-dlp."""
import json
import re
import subprocess
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class YouTubeServiceError(Exception):
    """Raised when a YouTube operation fails."""
    pass


class YouTubeService:
    """Service for downloading YouTube videos and extracting metadata."""

    @staticmethod
    def check_available() -> bool:
        """Check if yt-dlp is available on the system."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def get_version() -> Optional[str]:
        """Get yt-dlp version string."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_metadata(url: str) -> dict:
        """Fetch video metadata without downloading."""
        if not YouTubeService.check_available():
            raise YouTubeServiceError(
                "yt-dlp is not installed. Install with: pip install yt-dlp"
            )

        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--dump-json",
                    "--no-playlist",
                    "--no-warnings",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Failed to fetch video metadata"
                raise YouTubeServiceError(f"yt-dlp error: {error_msg}")

            metadata = json.loads(result.stdout)
            return {
                "title": metadata.get("title", "Unknown"),
                "duration": metadata.get("duration", 0),
                "width": metadata.get("width", 0),
                "height": metadata.get("height", 0),
                "fps": metadata.get("fps", 0),
                "youtube_id": metadata.get("id", ""),
            }
        except json.JSONDecodeError:
            raise YouTubeServiceError("Failed to parse video metadata")
        except subprocess.TimeoutExpired:
            raise YouTubeServiceError("Metadata fetch timed out after 60 seconds")

    @staticmethod
    def download_video(
        url: str,
        output_dir: Path,
        max_resolution: int = 1080,
        filename_prefix: str = "video",
    ) -> Path:
        """Download a YouTube video to the specified directory.

        Returns the path to the downloaded video file.
        """
        if not YouTubeService.check_available():
            raise YouTubeServiceError(
                "yt-dlp is not installed. Install with: pip install yt-dlp"
            )

        output_dir.mkdir(parents=True, exist_ok=True)

        # Build format string to cap resolution
        format_str = f"bestvideo[height<={max_resolution}]+bestaudio/best[height<={max_resolution}]/best"

        output_template = str(output_dir / f"{filename_prefix}_%(id)s.%(ext)s")

        try:
            logger.info(f"Downloading video: {url} to {output_dir}")
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--no-playlist",
                    "--no-warnings",
                    "--merge-output-format", "mp4",
                    "-f", format_str,
                    "-o", output_template,
                    "--no-overwrites",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=600,  # 10 min timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Download failed"
                raise YouTubeServiceError(f"Download error: {error_msg}")

            # Find the downloaded file
            for line in result.stdout.split("\n"):
                if "Destination:" in line or "has already been downloaded" in line:
                    # Extract path from output
                    pass

            # Search for the downloaded file
            mp4_files = list(output_dir.glob(f"{filename_prefix}_*.mp4"))
            if not mp4_files:
                # Try other extensions
                all_files = list(output_dir.glob(f"{filename_prefix}_*.*"))
                if all_files:
                    # Sort by modification time, pick newest
                    all_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    return all_files[0]
                raise YouTubeServiceError("Downloaded file not found")

            mp4_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            logger.info(f"Video downloaded: {mp4_files[0]}")
            return mp4_files[0]

        except subprocess.TimeoutExpired:
            raise YouTubeServiceError("Download timed out after 10 minutes")
