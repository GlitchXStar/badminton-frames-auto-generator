"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Link2, Loader2 } from "lucide-react";
import { EXTRACTION_INTERVALS, MAX_RESOLUTIONS } from "@/types";

interface VideoFormProps {
  onSubmit: (data: {
    youtube_url: string;
    extraction_interval: number;
    max_resolution: number;
  }) => Promise<void>;
}

export function VideoForm({ onSubmit }: VideoFormProps) {
  const [url, setUrl] = useState("");
  const [interval, setInterval] = useState(2);
  const [resolution, setResolution] = useState(1080);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await onSubmit({
        youtube_url: url.trim(),
        extraction_interval: interval,
        max_resolution: resolution,
      });
      setUrl("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to add video");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="youtube-url">YouTube URL</Label>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Link2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="youtube-url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="space-y-2 flex-1">
          <Label>Extraction Interval</Label>
          <Select
            value={String(interval)}
            onValueChange={(v) => setInterval(Number(v))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {EXTRACTION_INTERVALS.map((opt) => (
                <SelectItem key={opt.value} value={String(opt.value)}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2 flex-1">
          <Label>Max Resolution</Label>
          <Select
            value={String(resolution)}
            onValueChange={(v) => setResolution(Number(v))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {MAX_RESOLUTIONS.map((opt) => (
                <SelectItem key={opt.value} value={String(opt.value)}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <Button
        type="submit"
        disabled={loading || !url.trim()}
        className="bg-gradient-to-r from-emerald-600 to-teal-600"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Adding Video...
          </>
        ) : (
          "Add Video"
        )}
      </Button>
    </form>
  );
}
