// TypeScript types for Badminton Dataset Generator

export interface ProjectStats {
  total_videos: number;
  total_frames: number;
  candidates: number;
  duplicates: number;
  rejected: number;
  selected: number;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  target_images: number;
  status: string;
  created_at: string;
  updated_at: string | null;
  stats: ProjectStats | null;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

export interface Video {
  id: number;
  project_id: number;
  youtube_url: string;
  youtube_id: string | null;
  title: string | null;
  duration: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  extraction_interval?: number;
  max_resolution?: number;
  local_path: string | null;
  status: string;
  created_at: string;
  frame_count: number;
}

export interface VideoListResponse {
  videos: Video[];
  total: number;
}

export interface Frame {
  id: number;
  video_id: number;
  filename: string;
  filepath: string;
  timestamp: number | null;
  frame_number: number | null;
  width: number | null;
  height: number | null;
  blur_score: number | null;
  quality_score: number | null;
  sha256: string | null;
  phash: string | null;
  is_duplicate: boolean;
  is_rejected: boolean;
  is_selected: boolean;
  rejection_reason: string | null;
  selection_reason: string | null;
  created_at: string;
  image_url: string | null;
}

export interface FrameListResponse {
  frames: Frame[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ProcessingJob {
  id: number;
  project_id: number;
  video_id: number | null;
  job_type: string;
  status: string;
  progress: number;
  total_items: number;
  processed_items: number;
  message: string | null;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  ffmpeg: string;
  ytdlp: string;
  data_dir: string;
}

export interface ExportResponse {
  export_id: string;
  filename: string;
  image_count: number;
  status: string;
  message: string;
}

export type FrameStatus = 'all' | 'selected' | 'rejected' | 'duplicate' | 'candidate';

export const REJECTION_REASONS = [
  'Too blurry',
  'Poor resolution',
  'No useful players',
  'Feet not visible',
  'Broadcast graphic',
  'Duplicate',
  'Other',
] as const;

export const EXTRACTION_INTERVALS = [
  { value: 0.033, label: '0.033s (~30 fps - Every Frame)' },
  { value: 0.04, label: '0.04s (25 fps)' },
  { value: 0.05, label: '0.05s (20 fps)' },
  { value: 0.1, label: '0.1s (10 fps)' },
  { value: 0.25, label: '0.25s (4 fps)' },
  { value: 0.5, label: '0.5s (2 fps)' },
  { value: 0.75, label: '0.75s' },
  { value: 1, label: '1 second (1 fps)' },
  { value: 2, label: '2 seconds' },
  { value: 3, label: '3 seconds' },
  { value: 5, label: '5 seconds' },
] as const;

export const MAX_RESOLUTIONS = [
  { value: 720, label: '720p' },
  { value: 1080, label: '1080p' },
] as const;
