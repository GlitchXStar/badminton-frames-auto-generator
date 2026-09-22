"""Image utility functions for testing and thumbnails."""
import io
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_test_image(
    width: int = 1280,
    height: int = 720,
    color: Optional[tuple] = None,
    noise: bool = True,
) -> Image.Image:
    """Generate a test image with optional noise for testing the pipeline.

    Args:
        width: Image width
        height: Image height
        color: Base RGB color tuple; random if None
        noise: Whether to add random noise

    Returns:
        PIL Image object
    """
    if color is None:
        # Random greenish color to simulate a badminton court
        color = (
            np.random.randint(30, 100),
            np.random.randint(120, 200),
            np.random.randint(50, 120),
        )

    img_array = np.full((height, width, 3), color, dtype=np.uint8)

    if noise:
        noise_array = np.random.randint(-30, 30, (height, width, 3), dtype=np.int16)
        img_array = np.clip(img_array.astype(np.int16) + noise_array, 0, 255).astype(np.uint8)

    return Image.fromarray(img_array, "RGB")


def save_test_images(
    output_dir: Path,
    count: int = 10,
    prefix: str = "test",
    width: int = 1280,
    height: int = 720,
) -> list[Path]:
    """Generate and save multiple test images for pipeline testing.

    Returns list of saved image paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    for i in range(count):
        img = generate_test_image(width=width, height=height)
        filename = f"{prefix}_{i + 1:06d}.jpg"
        filepath = output_dir / filename
        img.save(filepath, "JPEG", quality=95)
        paths.append(filepath)

    logger.info(f"Generated {count} test images in {output_dir}")
    return paths


def create_thumbnail(image_path: Path, size: tuple[int, int] = (320, 180)) -> Optional[bytes]:
    """Create a thumbnail of an image and return as bytes."""
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error creating thumbnail for {image_path}: {e}")
        return None
