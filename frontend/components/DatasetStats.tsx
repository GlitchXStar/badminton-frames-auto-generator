"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
  Video, ImageIcon, CheckCircle2, XCircle, Copy, Target,
} from "lucide-react";
import type { ProjectStats } from "@/types";

interface DatasetStatsProps {
  stats: ProjectStats | null;
  target: number;
}

export function DatasetStats({ stats, target }: DatasetStatsProps) {
  if (!stats) return null;

  const items = [
    { icon: Video, label: "Videos", value: stats.total_videos, color: "text-blue-400" },
    { icon: ImageIcon, label: "Total Frames Generated", value: stats.total_frames, color: "text-purple-400" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-2 lg:grid-cols-2">
      {items.map((item) => (
        <Card key={item.label} className="border-border/50 bg-card/50">
          <CardContent className="flex flex-col items-center gap-1.5 py-4">
            <item.icon className={`h-5 w-5 ${item.color}`} />
            <span className="text-xl font-bold">{item.value}</span>
            <span className="text-[11px] text-muted-foreground">{item.label}</span>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
