# Badminton Dataset Generator

A local full-stack application for collecting, filtering, curating, and exporting badminton match footage frames for manual CVAT annotation.

## Purpose

This tool helps collect approximately **2,000 new images** from YouTube badminton match footage for shoe detection annotation. The images are intentionally **unannotated** — CVAT is used later for manual shoe annotation.

**Workflow:** YouTube → Download → Frame Extraction → Quality Filter → Duplicate Detection → Diversity Selection → Review → CVAT Export

## Architecture

```
┌─────────────────────┐     ┌──────────────────────────┐
│  Next.js Frontend   │────▶│   FastAPI Backend         │
│  (port 3000)        │     │   (port 8000)             │
│  - Dashboard        │     │   - REST API              │
│  - Project View     │     │   - SQLite Database       │
│  - Frame Gallery    │     │   - Processing Pipeline   │
│  - Export Panel     │     │   - yt-dlp + FFmpeg        │
└─────────────────────┘     └──────────────────────────┘
```

## Requirements

- **Python** 3.10+
- **Node.js** 18+
- **FFmpeg** (for frame extraction)
- **yt-dlp** (for YouTube downloads)

## Windows Installation

### 1. FFmpeg

```powershell
# Option A: Using winget
winget install Gyan.FFmpeg

# Option B: Manual download
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

Verify: `ffmpeg -version`

### 2. yt-dlp

```powershell
pip install yt-dlp
```

Verify: `yt-dlp --version`

### 3. Backend Setup

```powershell
cd D:\Badminton_Shoe_Detection\badminton-dataset-generator\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup

```powershell
cd D:\Badminton_Shoe_Detection\badminton-dataset-generator\frontend

# Install dependencies
npm install
```

## Environment Variables

Copy `.env.example` to `.env` in the backend directory:

```powershell
copy .env.example backend\.env
```

Key variables:
- `FRONTEND_URL` — CORS origin (default: `http://localhost:3000`)
- `BLUR_THRESHOLD` — Laplacian variance threshold (default: `100.0`)
- `PHASH_SIMILARITY_THRESHOLD` — Hamming distance for near-duplicates (default: `8`)

## Running

### Start Backend

```powershell
cd D:\Badminton_Shoe_Detection\badminton-dataset-generator\backend
.\venv\Scripts\activate
python run.py
```

Backend runs at: **http://localhost:8000**
Swagger docs: **http://localhost:8000/docs**

### Start Frontend

```powershell
cd D:\Badminton_Shoe_Detection\badminton-dataset-generator\frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

## Usage

### 1. Create a Project

- Click **New Project** on the dashboard
- Enter a name (e.g., "Member 1 Batch") and target count (e.g., 500)

### 2. Add YouTube Video

- Open the project
- Paste a YouTube badminton match URL
- Select extraction interval (default: 2 seconds)
- Select max resolution (default: 1080p)
- Click **Add Video**

### 3. Process Frames

- Click **Process** on the video card
- Watch the pipeline progress:
  - ✓ Downloading video
  - ✓ Extracting frames
  - ✓ Quality filtering
  - ✓ Duplicate detection
  - ✓ Diversity selection

### 4. Review Frames

- Click **Review Frames** to open the gallery
- Filter by status: All, Candidates, Selected, Rejected, Duplicates
- Click a frame for full preview
- Use bulk actions: Select All, Reject All, Reset
- Individual actions: Select, Reject, Reset

### 5. Export CVAT Batch

- When you have enough selected images, click **Export CVAT Batch**
- A ZIP file is generated containing:
  - `images/` — Unannotated JPEG images with sequential names
  - `metadata/source_manifest.csv` — Per-image metadata
  - `metadata/dataset_report.json` — Aggregate statistics
  - `README.txt` — Import instructions for CVAT

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install FFmpeg and add to PATH |
| yt-dlp not found | `pip install yt-dlp` |
| Backend won't start | Check Python venv is activated |
| Frontend won't start | Run `npm install` in frontend/ |
| CORS errors | Ensure backend is running on port 8000 |
| Processing stuck | Check backend console for errors |
| Video download fails | Verify yt-dlp version: `yt-dlp -U` |
| Frames not loading | Check data/frames/ directory exists |

## Running Tests

```powershell
cd backend
.\venv\Scripts\activate
pytest tests/ -v
```

## Dependency Check

```powershell
python scripts/check_dependencies.py
```

## Project Structure

```
badminton-dataset-generator/
├── frontend/          # Next.js + TypeScript + Tailwind + shadcn/ui
├── backend/           # FastAPI + SQLAlchemy + SQLite
├── data/              # Videos, frames, exports (gitignored)
├── scripts/           # Utility scripts
├── .env.example       # Environment template
└── README.md          # This file
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui, Lucide |
| Backend | Python, FastAPI, SQLAlchemy, SQLite, Pydantic |
| Video | yt-dlp, FFmpeg |
| Image | OpenCV, Pillow, NumPy, ImageHash |
