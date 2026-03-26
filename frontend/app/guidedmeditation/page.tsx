"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, Sparkles, Loader2, Play } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Meditation = {
  id: string;
  title: string;
  duration_minutes: number;
  category: string;
  description: string;
  mood_tags: string[];
};

const DURATION_TABS = ["5", "10", "15"] as const;
const DURATION_LABELS: Record<string, string> = { "5": "5 min", "10": "10 min", "15": "15 min" };

const TAG_COLORS: Record<string, string> = {
  anxious: "bg-rose-500/15 text-rose-300",
  stressed: "bg-orange-500/15 text-orange-300",
  sad: "bg-blue-500/15 text-blue-300",
  tired: "bg-amber-500/15 text-amber-300",
  unfocused: "bg-purple-500/15 text-purple-300",
  angry: "bg-red-500/15 text-red-300",
  overwhelmed: "bg-orange-500/15 text-orange-300",
  low: "bg-blue-500/15 text-blue-300",
  neutral: "bg-gray-500/15 text-gray-300",
  lonely: "bg-indigo-500/15 text-indigo-300",
  frustrated: "bg-red-500/15 text-red-300",
  restless: "bg-amber-500/15 text-amber-300",
  disconnected: "bg-slate-500/15 text-slate-300",
  hurt: "bg-rose-500/15 text-rose-300",
  wired: "bg-yellow-500/15 text-yellow-300",
  self_critical: "bg-pink-500/15 text-pink-300",
  distracted: "bg-purple-500/15 text-purple-300",
  scattered: "bg-violet-500/15 text-violet-300",
};

export default function GuidedMeditationPage() {
  const [recommended, setRecommended] = useState<Meditation[]>([]);
  const [library, setLibrary] = useState<Record<string, Meditation[]>>({});
  const [activeTab, setActiveTab] = useState<string>("5");
  const [loading, setLoading] = useState(true);

  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [recRes, libRes] = await Promise.all([
          fetch(`${API}/api/v1/meditation/recommended`, { headers }),
          fetch(`${API}/api/v1/meditation/library`, { headers }),
        ]);
        if (recRes.ok) setRecommended((await recRes.json()).meditations || []);
        if (libRes.ok) setLibrary((await libRes.json()).groups || {});
      } catch { /* offline */ }
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-24">
      <div className="mb-10 text-center space-y-2">
        <Sparkles className="mx-auto h-8 w-8 text-teal-400" />
        <h1 className="text-3xl font-bold tracking-tight">Guided Meditation</h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Choose a session that matches how you feel. Breathe, listen, and let go.
        </p>
      </div>

      {recommended.length > 0 && (
        <div className="mb-12">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-teal-400" /> Recommended for You
          </h2>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {recommended.map((m) => (
              <MeditationCard key={m.id} meditation={m} featured />
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-4">All Sessions</h2>
        <div className="flex gap-2 mb-6">
          {DURATION_TABS.map((t) => (
            <Button key={t} size="sm" variant={activeTab === t ? "default" : "outline"} onClick={() => setActiveTab(t)}>
              {DURATION_LABELS[t]}
            </Button>
          ))}
        </div>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {(library[activeTab] || []).map((m) => (
            <MeditationCard key={m.id} meditation={m} />
          ))}
          {!(library[activeTab] || []).length && (
            <p className="col-span-3 text-center text-muted-foreground py-8">No sessions for this duration.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function MeditationCard({ meditation: m, featured }: { meditation: Meditation; featured?: boolean }) {
  return (
    <Link href={`/guidedmeditation/${m.id}`}>
      <Card className={`h-full transition-all hover:border-teal-500/50 hover:shadow-lg cursor-pointer ${featured ? "border-teal-500/30 bg-teal-500/5" : ""}`}>
        <CardContent className="p-5 flex flex-col gap-3 h-full">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold">{m.title}</h3>
              <p className="text-xs text-muted-foreground">{m.category}</p>
            </div>
            <Badge variant="outline" className="shrink-0 text-xs">
              <Clock className="mr-1 h-3 w-3" /> {m.duration_minutes}m
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground flex-1">{m.description}</p>
          <div className="flex flex-wrap gap-1.5">
            {m.mood_tags.slice(0, 4).map((tag) => (
              <span key={tag} className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${TAG_COLORS[tag] || "bg-muted text-muted-foreground"}`}>
                {tag}
              </span>
            ))}
          </div>
          <span className="inline-flex items-center gap-1 text-xs text-teal-400 font-medium pt-1">
            <Play className="h-3 w-3" /> Start session
          </span>
        </CardContent>
      </Card>
    </Link>
  );
}
