"use client";

import { useEffect, useState, useCallback, use } from "react";
import Link from "next/link";
import {
  ArrowLeft, CheckCircle2, XCircle, RotateCcw,
  Filter, Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import {
  getProject, getFrames, updateFrame, bulkFrameAction, getFrameImageUrl,
  exportProject, getExportDownloadUrl,
} from "@/lib/api";
import type { Project, Frame, FrameStatus } from "@/types";
import { REJECTION_REASONS } from "@/types";
import { FrameCard } from "@/components/FrameCard";

export default function ReviewPage({ params }: { params: Promise<{ projectId: string }> }) {
  const resolvedParams = use(params);
  const projectId = Number(resolvedParams.projectId);

  const [project, setProject] = useState<Project | null>(null);
  const [frames, setFrames] = useState<Frame[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<FrameStatus>("all");
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [previewFrame, setPreviewFrame] = useState<Frame | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [p, f] = await Promise.all([
        getProject(projectId),
        getFrames(projectId, {
          status: statusFilter === "all" ? undefined : statusFilter,
          page: 1,
          page_size: 10000,
        }),
      ]);
      setProject(p);
      setFrames(f.frames);
      setTotal(f.total);
    } catch {
      // handle error
    } finally {
      setLoading(false);
    }
  }, [projectId, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(frames.map((f) => f.id)));
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  const handleBulk = async (action: "select" | "reject" | "reset", reason?: string) => {
    if (selectedIds.size === 0) return;
    try {
      await bulkFrameAction(projectId, {
        frame_ids: Array.from(selectedIds),
        action,
        rejection_reason: reason,
      });
      setSelectedIds(new Set());
      await loadData();
    } catch {
      // handle
    }
  };

  const handleSingleAction = async (
    frameId: number,
    action: "select" | "reject" | "reset",
    reason?: string
  ) => {
    try {
      if (action === "select") {
        await updateFrame(frameId, { is_selected: true });
      } else if (action === "reject") {
        await updateFrame(frameId, { is_rejected: true, rejection_reason: reason });
      } else {
        await updateFrame(frameId, { is_selected: false, is_rejected: false });
      }
      await loadData();
    } catch {
      // handle
    }
  };

  const handleExport = async () => {
    try {
      const result = await exportProject(projectId);
      window.open(getExportDownloadUrl(result.export_id), "_blank");
    } catch {
      // handle
    }
  };

  const selected = project?.stats?.selected ?? 0;
  const target = project?.target_images ?? 500;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link href={`/projects/${projectId}`} className="hover:text-foreground transition-colors flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" />
          {project?.name || "Project"}
        </Link>
        <span>/</span>
        <span className="text-foreground font-medium">Frame Review</span>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant="outline">
          {total} frames generated
        </Badge>
      </div>

      {/* Frame grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Activity className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : frames.length === 0 ? (
        <div className="py-20 text-center text-muted-foreground">
          No frames found with current filter.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {frames.map((frame) => (
            <FrameCard
              key={frame.id}
              frame={frame}
              isChecked={selectedIds.has(frame.id)}
              onToggleCheck={() => toggleSelect(frame.id)}
              onPreview={() => setPreviewFrame(frame)}
              onAction={handleSingleAction}
            />
          ))}
        </div>
      )}

      {/* Preview dialog */}
      <Dialog open={!!previewFrame} onOpenChange={() => setPreviewFrame(null)}>
        <DialogContent className="max-w-3xl">
          {previewFrame && (
            <div className="space-y-4">
              <img
                src={getFrameImageUrl(previewFrame.id)}
                alt={previewFrame.filename}
                className="w-full rounded-lg"
              />
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><span className="text-muted-foreground">File:</span> {previewFrame.filename}</div>
                <div><span className="text-muted-foreground">Resolution:</span> {previewFrame.width}×{previewFrame.height}</div>
                <div><span className="text-muted-foreground">Timestamp:</span> {previewFrame.timestamp?.toFixed(1)}s</div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
