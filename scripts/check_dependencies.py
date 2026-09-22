#!/usr/bin/env python3
"""Check that all required dependencies are installed."""
import subprocess
import sys
import shutil


def check_command(name: str, args: list[str]) -> tuple[bool, str]:
    """Check if a command is available and return its version."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, version
        return False, "Error running command"
    except FileNotFoundError:
        return False, "Not found"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def main():
    print("=" * 60)
    print("  Badminton Dataset Generator — Dependency Check")
    print("=" * 60)
    print()

    all_ok = True

    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  ✓ Python          {py_version}")

    # Node.js
    ok, ver = check_command("node", ["node", "--version"])
    if ok:
        print(f"  ✓ Node.js         {ver}")
    else:
        print(f"  ✗ Node.js         {ver}")
        all_ok = False

    # npm
    ok, ver = check_command("npm", ["npm", "--version"])
    if ok:
        print(f"  ✓ npm             {ver}")
    else:
        print(f"  ✗ npm             {ver}")
        all_ok = False

    # FFmpeg
    ok, ver = check_command("ffmpeg", ["ffmpeg", "-version"])
    if ok:
        print(f"  ✓ FFmpeg          {ver}")
    else:
        print(f"  ✗ FFmpeg          {ver}")
        print("    Install: winget install Gyan.FFmpeg")
        print("    Or download from: https://ffmpeg.org/download.html")
        all_ok = False

    # yt-dlp
    ok, ver = check_command("yt-dlp", ["yt-dlp", "--version"])
    if ok:
        print(f"  ✓ yt-dlp          {ver}")
    else:
        print(f"  ✗ yt-dlp          {ver}")
        print("    Install: pip install yt-dlp")
        all_ok = False

    print()
    if all_ok:
        print("  All dependencies are available! ✓")
    else:
        print("  Some dependencies are missing. Please install them.")
    print()
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
