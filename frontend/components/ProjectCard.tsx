"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Video, ImageIcon, CheckCircle2, XCircle, Copy, Target,
} from "lucide-react";
import type { Project } from "@/types";

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const stats = project.stats;
  const selected = stats?.selected ?? 0;
  const target = project.target_images;
  const progress = target > 0 ? Math.min(100, (selected / target) * 100) : 0;

  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="group cursor-pointer border-border/50 bg-card/50 transition-all hover:border-emerald-500/30 hover:shadow-lg hover:shadow-emerald-500/5">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <CardTitle className="text-base font-semibold group-hover:text-emerald-400 transition-colors">
              {project.name}
            </CardTitle>
            <Badge variant={project.status === "active" ? "default" : "secondary"} className="text-xs">
              {project.status}
            </Badge>
          </div>
          {project.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
          )}
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-2 mt-4">
            <StatItem icon={Video} label="Videos" value={stats?.total_videos ?? 0} />
            <StatItem icon={ImageIcon} label="Total Frames" value={stats?.total_frames ?? 0} />
          </div>

          <p className="text-[10px] text-muted-foreground/60">
            Created {new Date(project.created_at).toLocaleDateString()}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}

function StatItem({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: number;
  color?: "emerald" | "red";
}) {
  const colorClass = color === "emerald"
    ? "text-emerald-400"
    : color === "red"
    ? "text-red-400"
    : "text-muted-foreground";

  return (
    <div className="flex flex-col items-center gap-0.5 rounded-lg bg-muted/30 p-2">
      <Icon className={`h-3.5 w-3.5 ${colorClass}`} />
      <span className="text-xs font-medium">{value}</span>
      <span className="text-[10px] text-muted-foreground">{label}</span>
    </div>
  );
}
