// API client for Badminton Dataset Generator backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// ===== Projects =====

import type {
  Project, ProjectListResponse, Video, VideoListResponse,
  Frame, FrameListResponse, ProcessingJob, HealthResponse,
  ExportResponse, FrameStatus,
} from '@/types';

export async function getHealth(): Promise<HealthResponse> {
  return fetchAPI('/api/health');
}

export async function createProject(data: {
  name: string;
  target_images: number;
  description?: string;
}): Promise<Project> {
  return fetchAPI('/api/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getProjects(): Promise<ProjectListResponse> {
  return fetchAPI('/api/projects');
}

export async function getProject(id: number): Promise<Project> {
  return fetchAPI(`/api/projects/${id}`);
}

// ===== Videos =====

export async function addVideo(projectId: number, data: {
  youtube_url: string;
  extraction_interval: number;
  max_resolution: number;
}): Promise<Video> {
  return fetchAPI(`/api/projects/${projectId}/videos`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getVideos(projectId: number): Promise<VideoListResponse> {
  return fetchAPI(`/api/projects/${projectId}/videos`);
}

// ===== Processing =====

export async function processVideo(videoId: number, data?: {
  extraction_interval?: number;
  max_resolution?: number;
}): Promise<ProcessingJob> {
  return fetchAPI(`/api/videos/${videoId}/process`, {
    method: 'POST',
    body: JSON.stringify(data || {}),
  });
}

export async function getJobStatus(jobId: number): Promise<ProcessingJob> {
  return fetchAPI(`/api/jobs/${jobId}`);
}

// ===== Frames =====

export async function getFrames(
  projectId: number,
  params?: {
    status?: FrameStatus;
    video_id?: number;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }
): Promise<FrameListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.video_id) searchParams.set('video_id', String(params.video_id));
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.page_size) searchParams.set('page_size', String(params.page_size));
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by);
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order);

  const qs = searchParams.toString();
  return fetchAPI(`/api/projects/${projectId}/frames${qs ? `?${qs}` : ''}`);
}

export async function updateFrame(frameId: number, data: {
  is_selected?: boolean;
  is_rejected?: boolean;
  rejection_reason?: string;
}): Promise<Frame> {
  return fetchAPI(`/api/frames/${frameId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function bulkFrameAction(projectId: number, data: {
  frame_ids: number[];
  action: 'select' | 'reject' | 'reset';
  rejection_reason?: string;
}): Promise<{ updated: number; action: string }> {
  return fetchAPI(`/api/projects/${projectId}/frames/bulk`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getFrameImageUrl(frameId: number): string {
  return `${API_BASE}/api/frames/${frameId}/image`;
}

// ===== Exports =====

export async function exportProject(projectId: number, data?: {
  batch_name?: string;
  max_images?: number;
}): Promise<ExportResponse> {
  return fetchAPI(`/api/projects/${projectId}/export`, {
    method: 'POST',
    body: JSON.stringify(data || {}),
  });
}

export function getExportDownloadUrl(exportId: string): string {
  return `${API_BASE}/api/exports/${exportId}/download`;
}
