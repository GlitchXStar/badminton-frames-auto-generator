"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { ProjectStats } from "@/types";

interface ExportPanelProps {
  stats: ProjectStats | null;
  target: number;
  onExport: () => void;
}

export function ExportPanel({ stats, target, onExport }: ExportPanelProps) {
  const selected = stats?.selected ?? 0;
  const diff = target - selected;
  const ready = selected >= target;

  return (
    <Card className="border-border/50 bg-card/50">
      <CardContent className="flex flex-col gap-4 py-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          {ready ? (
            <CheckCircle2 className="h-6 w-6 text-emerald-400" />
          ) : (
            <AlertTriangle className="h-6 w-6 text-amber-400" />
          )}
          <div>
            <p className="font-medium">
              Selected: {selected} / {target}
            </p>
            <p className="text-sm text-muted-foreground">
              {ready
                ? "Ready for CVAT export."
                : `Need ${diff} more images.`}
            </p>
          </div>
        </div>
        <Button
          onClick={onExport}
          disabled={selected === 0}
          className="bg-gradient-to-r from-emerald-600 to-teal-600"
        >
          <Download className="mr-2 h-4 w-4" />
          Export CVAT Batch
        </Button>
      </CardContent>
    </Card>
  );
}
