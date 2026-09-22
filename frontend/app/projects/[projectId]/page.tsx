"use client";

import { useEffect, useState, useCallback, use } from "react";
import Link from "next/link";
import {
  Video as VideoIcon, ImageIcon, CheckCircle2, XCircle, Copy,
  Target, ArrowLeft, Download, RefreshCw, Play, Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  getProject, getVideos, addVideo, processVideo, getJobStatus, exportProject,
  getExportDownloadUrl,
} from "@/lib/api";
import type { Project, Video, ProcessingJob, ExportResponse } from "@/types";
import { VideoForm } from "@/components/VideoForm";
import { ProcessingProgress } from "@/components/ProcessingProgress";
import { DatasetStats } from "@/components/DatasetStats";
import { ExportPanel } from "@/components/ExportPanel";

export default function ProjectPage({ params }: { params: Promise<{ projectId: string }> }) {
  const resolvedParams = use(params);
  const projectId = Number(resolvedParams.projectId);

  const [project, setProject] = useState<Project | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [activeJob, setActiveJob] = useState<ProcessingJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [p, v] = await Promise.all([
        getProject(projectId),
        getVideos(projectId),
      ]);
      setProject(p);
      setVideos(v.videos);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Poll active job
  useEffect(() => {
    if (!activeJob || activeJob.status === "completed" || activeJob.status === "failed") return;

    const interval = setInterval(async () => {
      try {
        const job = await getJobStatus(activeJob.id);
        setActiveJob(job);
        if (job.status === "completed" || job.status === "failed") {
          await loadData();
        }
      } catch {
        // ignore polling errors
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeJob, loadData]);

  const handleAddVideo = async (data: { youtube_url: string; extraction_interval: number; max_resolution: number }) => {
    try {
      setError(null);
      const newVid = await addVideo(projectId, data);
      const job = await processVideo(newVid.id, {
        extraction_interval: data.extraction_interval,
        max_resolution: data.max_resolution,
      });
      setActiveJob(job);
      await loadData();
    } catch (err: unknown) {
      throw err;
    }
  };

  const handleProcess = async (video: Video) => {
    try {
      setError(null);
      const job = await processVideo(video.id, {
        extraction_interval: video.extraction_interval || 2.0,
        max_resolution: video.max_resolution || 1080,
      });
      setActiveJob(job);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to start processing");
    }
  };

  const handleExport = async () => {
    try {
      setError(null);
      const result = await exportProject(projectId);
      window.open(getExportDownloadUrl(result.export_id), "_blank");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Activity className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!project) {
    return <div className="py-10 text-center text-muted-foreground">Project not found</div>;
  }

  const stats = project.stats;
  const selected = stats?.selected ?? 0;
  const target = project.target_images;
  const progress = target > 0 ? Math.min(100, (selected / target) * 100) : 0;

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground transition-colors flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" />
          Projects
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">{project.name}</span>
      </div>

      {/* Project header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">{project.name}</h2>
          {project.description && (
            <p className="mt-1 text-muted-foreground">{project.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <Link href={`/projects/${project.id}/review`}>
            <Button variant="outline">
              <ImageIcon className="mr-2 h-4 w-4" />
              Review Frames
            </Button>
          </Link>
          <Button
            onClick={handleExport}
            disabled={(stats?.total_frames ?? 0) === 0}
            className="bg-gradient-to-r from-emerald-600 to-teal-600"
          >
            <Download className="mr-2 h-4 w-4" />
            Export CVAT Batch
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-400 ring-1 ring-red-500/20">
          {error}
        </div>
      )}

      {/* Stats */}
      <DatasetStats stats={stats} target={target} />

      {/* Active processing */}
      {activeJob && activeJob.status !== "completed" && activeJob.status !== "failed" && (
        <ProcessingProgress job={activeJob} />
      )}

      {/* Add video form */}
      <Card className="border-border/50 bg-card/50">
        <CardHeader>
          <CardTitle className="text-base">Add YouTube Video</CardTitle>
        </CardHeader>
        <CardContent>
          <VideoForm onSubmit={handleAddVideo} />
        </CardContent>
      </Card>

      {/* Videos list */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Videos ({videos.length})</h3>
        {videos.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border/50 py-10 text-center text-muted-foreground">
            No videos added yet. Add a YouTube URL above to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {videos.map((video) => (
              <Card key={video.id} className="border-border/50 bg-card/50">
                <CardContent className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{video.title || "Untitled"}</p>
                    <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                      {video.duration && (
                        <span>{Math.floor(video.duration / 60)}:{String(Math.floor(video.duration % 60)).padStart(2, '0')}</span>
                      )}
                      {video.width && video.height && <span>{video.width}×{video.height}</span>}
                      <span>{video.frame_count} frames</span>
                      <span>Interval: {video.extraction_interval ?? 2.0}s</span>
                      <Badge variant="secondary" className="text-[10px]">{video.status}</Badge>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleProcess(video)}
                    disabled={video.status === "processed" || !!activeJob}
                  >
                    {video.status === "processed" ? (
                      <>
                        <CheckCircle2 className="mr-1.5 h-3.5 w-3.5 text-emerald-400" />
                        Processed
                      </>
                    ) : (
                      <>
                        <Play className="mr-1.5 h-3.5 w-3.5" />
                        Process
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
