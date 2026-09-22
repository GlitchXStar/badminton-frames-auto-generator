"""FFmpeg frame extraction service."""
import subprocess
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class FFmpegServiceError(Exception):
    """Raised when an FFmpeg operation fails."""
    pass


class FFmpegService:
    """Service for extracting frames from video files using FFmpeg."""

    @staticmethod
    def check_available() -> bool:
        """Check if FFmpeg is available on the system."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def get_version() -> Optional[str]:
        """Get FFmpeg version string."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                first_line = result.stdout.split("\n")[0]
                return first_line.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    @staticmethod
    def get_video_info(video_path: Path) -> dict:
        """Get video information using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_streams",
                    "-show_format",
                    str(video_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                video_stream = None
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "video":
                        video_stream = stream
                        break

                if video_stream:
                    # Parse fps from r_frame_rate (e.g. "30/1")
                    fps_str = video_stream.get("r_frame_rate", "30/1")
                    try:
                        num, den = fps_str.split("/")
                        fps = float(num) / float(den)
                    except (ValueError, ZeroDivisionError):
                        fps = 30.0

                    return {
                        "width": int(video_stream.get("width", 0)),
                        "height": int(video_stream.get("height", 0)),
                        "fps": fps,
                        "duration": float(data.get("format", {}).get("duration", 0)),
                    }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return {}

    @staticmethod
    def extract_frames(
        video_path: Path,
        output_dir: Path,
        interval_seconds: float = 2.0,
        max_resolution: int = 1080,
        filename_prefix: str = "frame",
        jpeg_quality: int = 2,
    ) -> list[Path]:
        """Extract frames from a video at specified intervals.

        Args:
            video_path: Path to the video file
            output_dir: Directory to save extracted frames
            interval_seconds: Seconds between frame captures (e.g. 0.25, 0.5, 0.75, 1, 2)
            max_resolution: Maximum height in pixels (no upscale)
            filename_prefix: Prefix for frame filenames
            jpeg_quality: JPEG quality (2=high, 31=low)

        Returns:
            List of paths to extracted frame images
        """
        if not FFmpegService.check_available():
            raise FFmpegServiceError(
                "FFmpeg is not installed. Please install FFmpeg and ensure it's on PATH."
            )

        if not video_path.exists():
            raise FFmpegServiceError(f"Video file not found: {video_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Build scale filter: scale down to max_resolution if larger, no upscale
        scale_filter = f"scale=-2:'min({max_resolution},ih)'"

        # Output pattern
        output_pattern = str(output_dir / f"{filename_prefix}_%06d.jpg")

        # FPS filter for extraction interval
        fps_val = 1.0 / interval_seconds
        fps_filter = f"fps={fps_val:.4f}".rstrip('0').rstrip('.')

        # Combine filters
        vf_filter = f"{fps_filter},{scale_filter}"

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", vf_filter,
            "-q:v", str(jpeg_quality),
            "-vsync", "vfr",
            "-y",  # overwrite
            output_pattern,
        ]

        logger.info(f"Extracting frames: interval={interval_seconds}s, max_res={max_resolution}p")
        logger.info(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 min timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr[-500:] if result.stderr else "Frame extraction failed"
                raise FFmpegServiceError(f"FFmpeg error: {error_msg}")

        except subprocess.TimeoutExpired:
            raise FFmpegServiceError("Frame extraction timed out after 10 minutes")

        # Collect extracted frames
        frames = sorted(output_dir.glob(f"{filename_prefix}_*.jpg"))
        logger.info(f"Extracted {len(frames)} frames to {output_dir}")

        return frames
