"""File system utility functions."""
import re
import unicodedata
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """Sanitize a filename to be safe for all operating systems.

    Removes path traversal characters, normalizes unicode, and limits length.
    """
    # Normalize unicode
    filename = unicodedata.normalize("NFKD", filename)

    # Remove path separators and traversal
    filename = filename.replace("/", "_").replace("\\", "_").replace("..", "_")

    # Keep only safe characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > max_length:
        name, ext = split_filename(filename)
        filename = name[: max_length - len(ext) - 1] + ext

    return filename or "unnamed"


def split_filename(filename: str) -> tuple[str, str]:
    """Split filename into name and extension."""
    p = Path(filename)
    return p.stem, p.suffix


def ensure_unique_path(path: Path) -> Path:
    """If path exists, append a number to make it unique."""
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1

    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def get_disk_usage(path: Path) -> dict:
    """Get disk usage for a directory."""
    import shutil
    try:
        total, used, free = shutil.disk_usage(str(path))
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round(used / total * 100, 1),
        }
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return {}


def validate_path_safety(path: Path, allowed_base: Path) -> bool:
    """Validate that a path doesn't escape the allowed base directory."""
    try:
        resolved = path.resolve()
        base_resolved = allowed_base.resolve()
        return str(resolved).startswith(str(base_resolved))
    except Exception:
        return False
