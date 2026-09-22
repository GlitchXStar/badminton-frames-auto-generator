"use client";

import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { getFrameImageUrl } from "@/lib/api";
import type { Frame } from "@/types";

interface FrameCardProps {
  frame: Frame;
  isChecked: boolean;
  onToggleCheck: () => void;
  onPreview: () => void;
  onAction: (frameId: number, action: "select" | "reject" | "reset", reason?: string) => void;
}

export function FrameCard({ frame, isChecked, onToggleCheck, onPreview }: FrameCardProps) {
  return (
    <Card
      className="group relative cursor-pointer overflow-hidden border-border/50 bg-card/50 ring-2 ring-transparent transition-all hover:ring-emerald-500/30"
    >
      {/* Image */}
      <div className="aspect-video overflow-hidden" onClick={onPreview}>
        <img
          src={getFrameImageUrl(frame.id)}
          alt={frame.filename}
          className="h-full w-full object-cover transition-transform group-hover:scale-105"
          loading="lazy"
        />
      </div>

      {/* Info */}
      <div className="px-2 py-1.5">
        <div className="flex items-center justify-between text-[10px] text-muted-foreground">
          <span>{frame.timestamp?.toFixed(1)}s</span>
        </div>
      </div>
    </Card>
  );
}
