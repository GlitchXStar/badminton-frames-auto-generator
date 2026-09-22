"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import type { ProcessingJob } from "@/types";

interface ProcessingProgressProps {
  job: ProcessingJob;
}

const STAGES = [
  { key: "download", label: "Downloading video", threshold: 15 },
  { key: "extract", label: "Extracting frames", threshold: 40 },
  { key: "quality", label: "Quality filtering", threshold: 65 },
  { key: "duplicate", label: "Duplicate detection", threshold: 85 },
  { key: "select", label: "Selection", threshold: 100 },
];

export function ProcessingProgress({ job }: ProcessingProgressProps) {
  const isFailed = job.status === "failed";

  return (
    <Card className="border-emerald-500/20 bg-card/50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          {isFailed ? (
            <AlertCircle className="h-5 w-5 text-red-400" />
          ) : (
            <Loader2 className="h-5 w-5 animate-spin text-emerald-400" />
          )}
          Processing Pipeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={job.progress} className="h-2" />

        <div className="space-y-2">
          {STAGES.map((stage) => {
            const completed = job.progress >= stage.threshold;
            const active = !completed && job.progress >= (stage.threshold - 25);

            return (
              <div key={stage.key} className="flex items-center gap-3 text-sm">
                {completed ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 animate-spin text-amber-400" />
                ) : (
                  <div className="h-4 w-4 rounded-full border border-border/50" />
                )}
                <span className={completed ? "text-foreground" : "text-muted-foreground"}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>

        {job.message && (
          <p className="text-xs text-muted-foreground">{job.message}</p>
        )}

        {job.error && (
          <p className="text-xs text-red-400">{job.error}</p>
        )}
      </CardContent>
    </Card>
  );
}
