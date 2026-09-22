"""Diversity-aware frame selection service."""
from typing import Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class SelectionService:
    """Service for selecting diverse, high-quality frames from candidates."""

    @staticmethod
    def select_frames(
        candidates: list[dict],
        target_count: int,
        num_segments: int = 20,
    ) -> list[dict]:
        """Select diverse frames across the video timeline.

        Algorithm:
        1. Filter out rejected, duplicate frames
        2. Divide valid candidates by timestamp into segments
        3. Round-robin select from segments, preferring higher quality
        4. Stop when target_count reached

        Args:
            candidates: List of frame dicts with keys:
                id, timestamp, quality_score, is_duplicate, is_rejected, blur_score
            target_count: Number of frames to select
            num_segments: Number of timeline segments for diversity

        Returns:
            List of selected frame dicts
        """
        # Filter to valid candidates only
        valid = [
            f for f in candidates
            if not f.get("is_duplicate", False)
            and not f.get("is_rejected", False)
        ]

        if not valid:
            logger.warning("No valid candidate frames available for selection")
            return []

        logger.info(f"Selection: {len(valid)} valid candidates for target of {target_count}")

        if len(valid) <= target_count:
            logger.info(f"Not enough candidates ({len(valid)}) for target ({target_count}). Selecting all.")
            return valid

        # Sort by timestamp
        valid.sort(key=lambda f: f.get("timestamp", 0) or 0)

        # Divide into timeline segments
        if len(valid) > 0:
            min_ts = valid[0].get("timestamp", 0) or 0
            max_ts = valid[-1].get("timestamp", 0) or 0
            segment_duration = (max_ts - min_ts) / max(num_segments, 1) if max_ts > min_ts else 1.0
        else:
            segment_duration = 1.0
            min_ts = 0

        # Group frames into segments
        segments: list[list[dict]] = [[] for _ in range(num_segments)]
        for frame in valid:
            ts = frame.get("timestamp", 0) or 0
            seg_idx = int((ts - min_ts) / segment_duration) if segment_duration > 0 else 0
            seg_idx = min(seg_idx, num_segments - 1)
            segments[seg_idx].append(frame)

        # Sort each segment by quality (higher = better)
        for seg in segments:
            seg.sort(key=lambda f: f.get("quality_score", 0) or 0, reverse=True)

        # Round-robin select from segments
        selected: list[dict] = []
        selected_ids: set[int] = set()

        # Keep cycling through segments until target reached
        max_rounds = max(len(seg) for seg in segments if seg) if any(segments) else 0

        for round_num in range(max_rounds):
            if len(selected) >= target_count:
                break
            for seg in segments:
                if len(selected) >= target_count:
                    break
                if round_num < len(seg):
                    frame = seg[round_num]
                    if frame["id"] not in selected_ids:
                        selected.append(frame)
                        selected_ids.add(frame["id"])

        logger.info(f"Selected {len(selected)} frames from {num_segments} segments")
        return selected[:target_count]

    @staticmethod
    def get_selection_summary(
        total_frames: int,
        valid_candidates: int,
        selected_count: int,
        target_count: int,
    ) -> dict:
        """Generate a summary of the selection process."""
        shortfall = max(0, target_count - selected_count)
        return {
            "total_frames": total_frames,
            "valid_candidates": valid_candidates,
            "selected": selected_count,
            "target": target_count,
            "shortfall": shortfall,
            "enough": selected_count >= target_count,
            "message": (
                f"Ready for CVAT export ({selected_count} images)."
                if selected_count >= target_count
                else f"Need {shortfall} more images. Add another video or increase extraction density."
            ),
        }
