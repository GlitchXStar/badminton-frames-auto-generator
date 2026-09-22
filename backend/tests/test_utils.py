"""Tests for utility functions and services."""
import tempfile
from pathlib import Path

from app.utils.file_utils import sanitize_filename, validate_path_safety, ensure_unique_path
from app.services.duplicate_service import DuplicateService
from app.services.selection_service import SelectionService
from app.schemas.video import VideoCreate


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("hello world.jpg") == "hello world.jpg"
    assert sanitize_filename("../../../etc/passwd") == "______etc_passwd"
    assert sanitize_filename('file<>:"/\\|?*.jpg') == "file_________.jpg"
    assert sanitize_filename("") == "unnamed"
    assert sanitize_filename("...") == "_"


def test_path_safety():
    """Test path traversal prevention."""
    base = Path("D:/safe/dir")
    assert validate_path_safety(Path("D:/safe/dir/file.txt"), base) is True
    assert validate_path_safety(Path("D:/safe/dir/sub/file.txt"), base) is True


def test_ensure_unique_path():
    """Test unique path generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.txt"
        assert ensure_unique_path(path) == path  # Doesn't exist yet

        path.write_text("hello")
        unique = ensure_unique_path(path)
        assert unique != path
        assert "test_1" in unique.name


def test_url_validation():
    """Test YouTube URL validation and sub-second intervals."""
    # Valid URLs
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    ]
    for interval in [0.033, 0.04, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 5.0]:
        for url in valid_urls:
            data = VideoCreate(youtube_url=url, extraction_interval=interval, max_resolution=1080)
            assert data.youtube_url == url
            assert data.extraction_interval == interval

    # Invalid URLs
    import pytest
    invalid_urls = [
        "https://vimeo.com/12345",
        "not a url",
        "https://www.google.com",
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            VideoCreate(youtube_url=url, extraction_interval=2, max_resolution=1080)


def test_exact_duplicate_detection():
    """Test SHA-256 exact duplicate finding."""
    service = DuplicateService()
    hashes = {
        1: "abc123",
        2: "def456",
        3: "abc123",  # duplicate of 1
        4: "ghi789",
        5: "def456",  # duplicate of 2
    }
    dups = service.find_exact_duplicates(hashes)
    dup_ids = [d[0] for d in dups]
    assert 3 in dup_ids
    assert 5 in dup_ids


def test_selection_diversity():
    """Test diversity-aware frame selection."""
    candidates = [
        {"id": i, "timestamp": float(i * 2), "quality_score": 50.0 + i,
         "blur_score": 200.0, "is_duplicate": False, "is_rejected": False}
        for i in range(100)
    ]

    # Select 20 from 100
    selected = SelectionService.select_frames(candidates, target_count=20, num_segments=10)
    assert len(selected) == 20

    # Verify diversity — selected frames should span the timeline
    timestamps = [s["timestamp"] for s in selected]
    assert min(timestamps) < 20  # Some early frames
    assert max(timestamps) > 150  # Some late frames


def test_selection_insufficient_candidates():
    """Test selection when not enough candidates available."""
    candidates = [
        {"id": i, "timestamp": float(i), "quality_score": 50.0,
         "blur_score": 200.0, "is_duplicate": False, "is_rejected": False}
        for i in range(5)
    ]

    selected = SelectionService.select_frames(candidates, target_count=100)
    assert len(selected) == 5  # Returns all available


def test_selection_summary():
    """Test selection summary generation."""
    summary = SelectionService.get_selection_summary(
        total_frames=1000, valid_candidates=500, selected_count=450, target_count=500
    )
    assert summary["shortfall"] == 50
    assert not summary["enough"]
    assert "50 more" in summary["message"]

    summary_ok = SelectionService.get_selection_summary(
        total_frames=1000, valid_candidates=600, selected_count=500, target_count=500
    )
    assert summary_ok["enough"]
    assert "Ready" in summary_ok["message"]
