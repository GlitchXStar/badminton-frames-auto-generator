"""Image quality assessment service."""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageQualityService:
    """Service for assessing image quality and filtering bad frames."""

    def __init__(
        self,
        min_width: int = None,
        min_height: int = None,
        blur_threshold: float = None,
        black_threshold: float = None,
    ):
        self.min_width = min_width or settings.MIN_RESOLUTION_WIDTH
        self.min_height = min_height or settings.MIN_RESOLUTION_HEIGHT
        self.blur_threshold = blur_threshold or settings.BLUR_THRESHOLD
        self.black_threshold = black_threshold or settings.BLACK_FRAME_THRESHOLD

    def assess_image(self, image_path: Path) -> dict:
        """Assess the quality of an image file.

        Returns a dict with:
            - valid: bool
            - width, height: image dimensions
            - blur_score: Laplacian variance (higher = sharper)
            - quality_score: combined quality metric
            - rejection_reason: str or None
        """
        result = {
            "valid": True,
            "width": 0,
            "height": 0,
            "blur_score": 0.0,
            "quality_score": 0.0,
            "rejection_reason": None,
        }

        # 1. Try to load the image
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                result["valid"] = False
                result["rejection_reason"] = "Invalid image (cannot be read)"
                return result
        except Exception as e:
            logger.error(f"Error reading image {image_path}: {e}")
            result["valid"] = False
            result["rejection_reason"] = "Invalid image (corrupt file)"
            return result

        height, width = img.shape[:2]
        result["width"] = width
        result["height"] = height

        # 2. Minimum resolution check
        if width < self.min_width or height < self.min_height:
            result["valid"] = False
            result["rejection_reason"] = f"Low resolution ({width}x{height})"
            return result

        # 3. Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 4. Black/near-black frame detection
        mean_pixel = float(np.mean(gray))
        if mean_pixel < self.black_threshold:
            result["valid"] = False
            result["rejection_reason"] = f"Near-black frame (mean={mean_pixel:.1f})"
            return result

        # 5. Blur detection using Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())
        result["blur_score"] = blur_score

        if blur_score < self.blur_threshold:
            result["valid"] = False
            result["rejection_reason"] = f"Excessive blur (score={blur_score:.1f})"
            return result

        # 6. Compute overall quality score (normalized 0-100)
        # Combine blur score and brightness variance
        brightness_std = float(np.std(gray))
        quality = min(100.0, (blur_score / 10.0) + brightness_std)
        result["quality_score"] = round(quality, 2)

        return result

    def batch_assess(self, image_paths: list[Path]) -> list[dict]:
        """Assess quality for a batch of images."""
        results = []
        for path in image_paths:
            assessment = self.assess_image(path)
            assessment["path"] = str(path)
            results.append(assessment)
        return results
