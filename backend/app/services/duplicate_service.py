"""Duplicate detection service using SHA-256 and perceptual hashing."""
import hashlib
from pathlib import Path
from typing import Optional

import imagehash
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DuplicateService:
    """Service for detecting exact and near-duplicate images."""

    def __init__(self, phash_threshold: int = None):
        self.phash_threshold = phash_threshold or settings.PHASH_SIMILARITY_THRESHOLD

    @staticmethod
    def compute_sha256(image_path: Path) -> Optional[str]:
        """Compute SHA-256 hash of file contents."""
        try:
            sha256 = hashlib.sha256()
            with open(image_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing SHA-256 for {image_path}: {e}")
            return None

    @staticmethod
    def compute_phash(image_path: Path) -> Optional[str]:
        """Compute perceptual hash of an image."""
        try:
            img = Image.open(image_path)
            hash_val = imagehash.phash(img)
            return str(hash_val)
        except Exception as e:
            logger.error(f"Error computing pHash for {image_path}: {e}")
            return None

    def find_exact_duplicates(self, sha256_hashes: dict[int, str]) -> list[tuple[int, int]]:
        """Find exact duplicate pairs based on SHA-256 hashes.

        Args:
            sha256_hashes: Dict mapping frame_id -> sha256_hash

        Returns:
            List of (duplicate_id, original_id) tuples
        """
        hash_to_first: dict[str, int] = {}
        duplicates: list[tuple[int, int]] = []

        for frame_id, hash_val in sha256_hashes.items():
            if hash_val in hash_to_first:
                duplicates.append((frame_id, hash_to_first[hash_val]))
            else:
                hash_to_first[hash_val] = frame_id

        return duplicates

    def find_near_duplicates(self, phash_values: dict[int, str]) -> list[tuple[int, int, int]]:
        """Find near-duplicate pairs based on perceptual hash similarity.

        Args:
            phash_values: Dict mapping frame_id -> phash_string

        Returns:
            List of (duplicate_id, original_id, hamming_distance) tuples
        """
        items = list(phash_values.items())
        duplicates: list[tuple[int, int, int]] = []
        seen_duplicates: set[int] = set()

        for i in range(len(items)):
            if items[i][0] in seen_duplicates:
                continue
            for j in range(i + 1, len(items)):
                if items[j][0] in seen_duplicates:
                    continue
                try:
                    hash_a = imagehash.hex_to_hash(items[i][1])
                    hash_b = imagehash.hex_to_hash(items[j][1])
                    distance = hash_a - hash_b
                    if distance <= self.phash_threshold:
                        duplicates.append((items[j][0], items[i][0], distance))
                        seen_duplicates.add(items[j][0])
                except Exception:
                    continue

        return duplicates
