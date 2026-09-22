#!/usr/bin/env python3
"""Cleanup utility for removing project data safely."""
import shutil
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


def main():
    from app.core.config import settings
    from app.core.database import SessionLocal
    from app.models.project import Project

    print("=" * 60)
    print("  Badminton Dataset Generator — Project Cleanup")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        projects = db.query(Project).all()

        if not projects:
            print("  No projects found.")
            return

        print("  Available projects:")
        for p in projects:
            print(f"    [{p.id}] {p.name} (status: {p.status})")

        print()
        project_id = input("  Enter project ID to clean up (or 'q' to quit): ").strip()

        if project_id.lower() == "q":
            return

        try:
            project_id = int(project_id)
        except ValueError:
            print("  Invalid project ID.")
            return

        project = db.get(Project, project_id)
        if not project:
            print(f"  Project {project_id} not found.")
            return

        confirm = input(f"  Delete ALL data for '{project.name}'? (yes/no): ").strip()
        if confirm.lower() != "yes":
            print("  Cancelled.")
            return

        # Delete frame files
        frames_dir = settings.get_frames_dir()
        for video in project.videos:
            video_frames_dir = frames_dir / str(video.id)
            if video_frames_dir.exists():
                shutil.rmtree(video_frames_dir)
                print(f"  Deleted frames: {video_frames_dir}")

            # Delete video file
            if video.local_path:
                video_path = Path(video.local_path)
                if video_path.exists():
                    video_path.unlink()
                    print(f"  Deleted video: {video_path}")

        # Delete project from database (cascade deletes videos, frames, jobs)
        db.delete(project)
        db.commit()
        print(f"  Project '{project.name}' deleted successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
