"use client";

import React, { useEffect, useState, useMemo } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  TrendingUp, TrendingDown, Minus, Flame, BarChart3, Activity, Download,
  AlertTriangle, ArrowRight, Loader2,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Colours
const TEAL = "#14b8a6";
const CORAL = "#f97316";
const PURPLE = "#a855f7";
const PRIMARY = "#6366f1";
const FACET_COLORS: Record<string, string> = {
  mood: "#6366f1",
  stress: "#ef4444",
  energy: "#f59e0b",
  connection: "#14b8a6",
  motivation: "#a855f7",
};

type TimelinePoint = { date: string; mood_index: number; mood: number; stress: number; energy: number; connection: number; motivation: number };
type EmaPoint = { date: string; mood_index: number; ema7: number | null; ema14: number | null };
type FacetData = { average_all_time: number; average_recent: number; current: number; trend: string; percentile: number; sparkline: number[] };
type StreakData = { current_streak: number; longest_streak: number; total_checkins: number; mood_by_day: Record<string, number> };
type TrendData = { trend: string; zscore: number; ema7: number; mean_30d: number; message: string };

type Period = "week" | "month" | "3months";

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "improving" || trend === "IMPROVING") return <TrendingUp className="h-4 w-4 text-emerald-400" />;
  if (trend === "declining" || trend === "DECLINING") return <TrendingDown className="h-4 w-4 text-red-400" />;
  return <Minus className="h-4 w-4 text-muted-foreground" />;
}

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  if (!data.length) return null;
  const max = Math.max(...data, 1);
  const w = 100;
  const h = 28;
  const points = data.map((v, i) => `${(i / Math.max(data.length - 1, 1)) * w},${h - (v / max) * h}`).join(" ");
  return (
    <svg width={w} height={h} className="overflow-visible">
      <polyline points={points} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" />
    </svg>
  );
}

export default function MoodDashboard() {
  const [period, setPeriod] = useState<Period>("month");
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [emaData, setEmaData] = useState<EmaPoint[]>([]);
  const [facets, setFacets] = useState<Record<string, FacetData>>({});
  const [streaks, setStreaks] = useState<StreakData | null>(null);
  const [trends, setTrends] = useState<TrendData | null>(null);
  const [showEma, setShowEma] = useState(true);
  const [loading, setLoading] = useState(true);

  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  async function loadAll() {
    setLoading(true);
    try {
      const [tRes, eRes, fRes, sRes, trRes] = await Promise.all([
        fetch(`${API}/api/v1/analytics/dashboard/timeline?period=${period}`, { headers }),
        fetch(`${API}/api/v1/analytics/dashboard/ema`, { headers }),
        fetch(`${API}/api/v1/analytics/dashboard/facets`, { headers }),
        fetch(`${API}/api/v1/analytics/dashboard/streaks`, { headers }),
        fetch(`${API}/api/v1/analytics/dashboard/trends`, { headers }),
      ]);
      if (tRes.ok) setTimeline((await tRes.json()).data || []);
      if (eRes.ok) setEmaData((await eRes.json()).data || []);
      if (fRes.ok) setFacets((await fRes.json()).facets || {});
      if (sRes.ok) setStreaks(await sRes.json());
      if (trRes.ok) setTrends(await trRes.json());
    } catch { /* offline */ }
    setLoading(false);
  }

  useEffect(() => { loadAll(); }, [period]);

  async function handleExport() {
    try {
      const res = await fetch(`${API}/api/v1/analytics/dashboard/export?period=${period}`, { headers });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `superserene_report_${period}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch { /* */ }
  }

  // Merge timeline + ema for chart
  const chartData = useMemo(() => {
    if (!emaData.length) return timeline;
    const emaMap = new Map(emaData.map((e) => [e.date, e]));
    return timeline.map((t) => {
      const e = emaMap.get(t.date);
      return { ...t, ema7: e?.ema7 ?? null, ema14: e?.ema14 ?? null };
    });
  }, [timeline, emaData]);

  // Mood by day bar data
  const dayBarData = useMemo(() => {
    if (!streaks) return [];
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((d) => ({
      day: d.slice(0, 3),
      mood: streaks.mood_by_day[d] || 0,
    }));
  }, [streaks]);

  const avgMoodWeek = useMemo(() => {
    const week = timeline.slice(-7);
    if (!week.length) return 0;
    return Math.round(week.reduce((s, d) => s + d.mood_index, 0) / week.length);
  }, [timeline]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 pb-20 pt-24">
      {/* Trend alert banner */}
      {trends?.trend === "DECLINING" && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-5 py-3 text-sm">
          <AlertTriangle className="h-5 w-5 shrink-0 text-yellow-400" />
          <span className="flex-1 text-yellow-200">
            {trends.message}
          </span>
          <a
            href="/moodindex"
            className="shrink-0 rounded-lg bg-yellow-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-yellow-600 transition-colors"
          >
            Start a session <ArrowRight className="inline ml-1 h-3.5 w-3.5" />
          </a>
        </div>
      )}

      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <Badge variant="outline" className="mb-2 border-primary/30 bg-primary/5 text-primary">
            <Activity className="mr-1 h-4 w-4" /> Mood Analytics
          </Badge>
          <h1 className="text-3xl font-bold tracking-tight">Mood Dashboard</h1>
          <p className="text-muted-foreground">Track your emotional patterns over time.</p>
        </div>
        <Button variant="outline" onClick={handleExport}>
          <Download className="mr-1 h-4 w-4" /> Export PDF Report
        </Button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 mb-8">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Flame className="h-4 w-4 text-orange-400" /> Current Streak
            </div>
            <p className="text-2xl font-bold">{streaks?.current_streak ?? 0} <span className="text-sm font-normal text-muted-foreground">days</span></p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <BarChart3 className="h-4 w-4 text-primary" /> Avg Mood (Week)
            </div>
            <p className="text-2xl font-bold">{avgMoodWeek} <span className="text-sm font-normal text-muted-foreground">/ 100</span></p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <TrendIcon trend={trends?.trend || "STABLE"} /> Trend
            </div>
            <p className="text-2xl font-bold">{trends?.trend ?? "STABLE"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <Activity className="h-4 w-4 text-teal-400" /> Total Check-ins
            </div>
            <p className="text-2xl font-bold">{streaks?.total_checkins ?? 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Main chart */}
      <Card className="mb-8">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle>Mood Index</CardTitle>
            <CardDescription>Daily score over selected period</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {(["week", "month", "3months"] as Period[]).map((p) => (
              <Button key={p} size="sm" variant={period === p ? "default" : "outline"} onClick={() => setPeriod(p)}>
                {p === "3months" ? "3 Mo" : p.charAt(0).toUpperCase() + p.slice(1)}
              </Button>
            ))}
            <Button size="sm" variant={showEma ? "secondary" : "outline"} onClick={() => setShowEma(!showEma)}>
              EMA
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#666" tickFormatter={(v: string) => v.slice(5)} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#666" />
                <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #333", borderRadius: 8 }} labelStyle={{ color: "#aaa" }} />
                <Legend />
                <Line type="monotone" dataKey="mood_index" stroke={PRIMARY} strokeWidth={2} dot={false} name="Mood Index" />
                {showEma && <Line type="monotone" dataKey="ema7" stroke={TEAL} strokeWidth={1.5} strokeDasharray="4 2" dot={false} name="EMA 7-day" connectNulls />}
                {showEma && <Line type="monotone" dataKey="ema14" stroke={CORAL} strokeWidth={1.5} strokeDasharray="6 3" dot={false} name="EMA 14-day" connectNulls />}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        {/* Facet breakdown */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Facet Breakdown</CardTitle>
            <CardDescription>Individual dimensions of your well-being</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-5">
              {Object.entries(facets).map(([facet, data]) => (
                <div key={facet} className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: FACET_COLORS[facet] || "#888" }} />
                      <span className="text-sm font-medium capitalize">{facet}</span>
                      <TrendIcon trend={data.trend} />
                    </div>
                    <div className="flex items-center gap-3">
                      <MiniSparkline data={data.sparkline} color={FACET_COLORS[facet] || "#888"} />
                      <span className="text-sm font-semibold w-8 text-right">{data.current}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${Math.min((data.current / 5) * 100, 100)}%`, background: FACET_COLORS[facet] || "#888" }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-12 text-right">p{data.percentile}</span>
                  </div>
                </div>
              ))}
              {Object.keys(facets).length === 0 && (
                <p className="text-sm text-muted-foreground py-4 text-center">
                  Complete a few daily check-ins to see your facet breakdown.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Mood by day of week */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Mood by Day</CardTitle>
            <CardDescription>Average mood per weekday</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dayBarData} margin={{ top: 5, right: 5, bottom: 5, left: -15 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} stroke="#666" />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#666" />
                  <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #333", borderRadius: 8 }} />
                  <Bar dataKey="mood" radius={[4, 4, 0, 0]}>
                    {dayBarData.map((_, i) => (
                      <Cell key={i} fill={i < 5 ? PRIMARY : PURPLE} fillOpacity={0.8} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
