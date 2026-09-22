"use client";

import { useEffect, useState } from "react";
import { Plus, FolderOpen, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getProjects, createProject, getHealth } from "@/lib/api";
import type { Project, HealthResponse } from "@/types";
import { ProjectCard } from "@/components/ProjectCard";

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [target, setTarget] = useState(500);
  const [description, setDescription] = useState("");

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data.projects);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const loadHealth = async () => {
    try {
      const data = await getHealth();
      setHealth(data);
    } catch {
      // Backend not available
    }
  };

  useEffect(() => {
    loadProjects();
    loadHealth();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      await createProject({
        name: name.trim(),
        target_images: target,
        description: description.trim() || undefined,
      });
      setDialogOpen(false);
      setName("");
      setTarget(500);
      setDescription("");
      await loadProjects();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header section */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Projects</h2>
          <p className="text-muted-foreground">
            Manage your badminton dataset collection batches
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger
            render={
              <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500" />
            }
          >
            <Plus className="mr-2 h-4 w-4" />
            New Project
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div className="space-y-2">
                <Label htmlFor="project-name">Project Name</Label>
                <Input
                  id="project-name"
                  placeholder="e.g. Member 1 Batch"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-target">Target Images</Label>
                <Input
                  id="project-target"
                  type="number"
                  min={1}
                  max={10000}
                  value={target}
                  onChange={(e) => setTarget(Number(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-desc">Description (optional)</Label>
                <Textarea
                  id="project-desc"
                  placeholder="Optional description..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                />
              </div>
              {error && (
                <p className="text-sm text-red-400">{error}</p>
              )}
              <Button
                onClick={handleCreate}
                disabled={creating || !name.trim()}
                className="w-full bg-gradient-to-r from-emerald-600 to-teal-600"
              >
                {creating ? "Creating..." : "Create Project"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Health status */}
      {health && (
        <div className="flex flex-wrap gap-3">
          <StatusBadge label="Backend" status={health.status === "healthy"} />
          <StatusBadge label="FFmpeg" status={!health.ffmpeg.includes("not_installed")} />
          <StatusBadge label="yt-dlp" status={!health.ytdlp.includes("not_installed")} />
        </div>
      )}

      {/* Project grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Activity className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border/60 py-20">
          <FolderOpen className="mb-4 h-12 w-12 text-muted-foreground/50" />
          <h3 className="text-lg font-medium text-muted-foreground">No projects yet</h3>
          <p className="text-sm text-muted-foreground/70">Create your first project to get started</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ label, status }: { label: string; status: boolean }) {
  return (
    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${
      status
        ? "bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20"
        : "bg-red-500/10 text-red-400 ring-1 ring-red-500/20"
    }`}>
      <div className={`h-1.5 w-1.5 rounded-full ${status ? "bg-emerald-400" : "bg-red-400"}`} />
      {label}
    </div>
  );
}
