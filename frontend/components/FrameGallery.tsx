"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Frame } from "@/types";

interface FrameGalleryProps {
  frames: Frame[];
  onFrameSelect?: (frame: Frame) => void;
}

export function FrameGallery({ frames, onFrameSelect }: FrameGalleryProps) {
  if (frames.length === 0) {
    return (
      <div className="py-10 text-center text-muted-foreground">
        No frames to display.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {frames.map((frame) => (
        <div
          key={frame.id}
          className="cursor-pointer"
          onClick={() => onFrameSelect?.(frame)}
        >
          <Card className="overflow-hidden border-border/50 bg-card/50 hover:border-emerald-500/30 transition-all">
            <div className="aspect-video bg-muted">
              <img
                src={`http://localhost:8000/api/frames/${frame.id}/image`}
                alt={frame.filename}
                className="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
            <CardContent className="p-2 text-[10px] text-muted-foreground">
              {frame.timestamp?.toFixed(1)}s
            </CardContent>
          </Card>
        </div>
      ))}
    </div>
  );
}
