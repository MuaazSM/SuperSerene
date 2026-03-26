"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Play, Pause, SkipForward, SkipBack, ArrowLeft, Loader2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Step = { timestamp_seconds: number; instruction_text: string; breath_pattern: string | null };
type Meditation = {
  id: string;
  title: string;
  duration_minutes: number;
  category: string;
  description: string;
  steps: Step[];
};

type Phase = "pre" | "playing" | "post" | "done";

const MOOD_LABELS = ["", "Very Low", "Low", "Okay", "Good", "Great"];

// ── Component ────────────────────────────────────────────────────────────

export default function MeditationPlayer() {
  const params = useParams();
  const router = useRouter();
  const meditationId = params.id as string;

  const [meditation, setMeditation] = useState<Meditation | null>(null);
  const [loading, setLoading] = useState(true);
  const [phase, setPhase] = useState<Phase>("pre");
  const [preMood, setPreMood] = useState(0);
  const [postMood, setPostMood] = useState(0);
  const [delta, setDelta] = useState<number | null>(null);

  // Timer state
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Current step
  const [stepIdx, setStepIdx] = useState(0);

  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  // Load meditation
  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/v1/meditation/${meditationId}`, { headers });
        if (res.ok) setMeditation(await res.json());
      } catch { /* */ }
      setLoading(false);
    }
    load();
  }, [meditationId]);

  // Timer logic
  useEffect(() => {
    if (playing && meditation) {
      intervalRef.current = setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 1;
          if (next >= meditation.duration_minutes * 60) {
            setPlaying(false);
            setPhase("post");
            if (intervalRef.current) clearInterval(intervalRef.current);
            return meditation.duration_minutes * 60;
          }
          return next;
        });
      }, 1000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing, meditation]);

  // Update step index based on elapsed time
  useEffect(() => {
    if (!meditation) return;
    const steps = meditation.steps;
    let newIdx = 0;
    for (let i = steps.length - 1; i >= 0; i--) {
      if (elapsed >= steps[i].timestamp_seconds) {
        newIdx = i;
        break;
      }
    }
    setStepIdx(newIdx);
  }, [elapsed, meditation]);

  const totalSeconds = meditation ? meditation.duration_minutes * 60 : 0;
  const progress = totalSeconds > 0 ? elapsed / totalSeconds : 0;
  const currentStep = meditation?.steps[stepIdx];
  const hasBreath = currentStep?.breath_pattern != null;

  function togglePlay() {
    setPlaying((p) => !p);
  }

  function skipForward() {
    if (!meditation) return;
    const steps = meditation.steps;
    if (stepIdx < steps.length - 1) {
      setElapsed(steps[stepIdx + 1].timestamp_seconds);
    }
  }

  function skipBack() {
    if (!meditation) return;
    const steps = meditation.steps;
    if (stepIdx > 0) {
      setElapsed(steps[stepIdx - 1].timestamp_seconds);
    }
  }

  function startSession() {
    if (preMood < 1) return;
    setPhase("playing");
    setElapsed(0);
    setPlaying(true);
  }

  async function submitPost() {
    if (postMood < 1 || !meditation) return;
    try {
      const res = await fetch(`${API}/api/v1/meditation/${meditationId}/complete`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ pre_mood: preMood, post_mood: postMood }),
      });
      if (res.ok) {
        const data = await res.json();
        setDelta(data.delta);
      } else {
        setDelta(postMood - preMood);
      }
    } catch {
      setDelta(postMood - preMood);
    }
    setPhase("done");
  }

  function formatTime(s: number) {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  }

  // ── Loading ────────────────────────────────────────────────────────────
  if (loading || !meditation) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "#0F1B2D" }}>
        <Loader2 className="h-8 w-8 animate-spin text-teal-400" />
      </div>
    );
  }

  // ── Pre-session mood ───────────────────────────────────────────────────
  if (phase === "pre") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-6" style={{ background: "#0F1B2D" }}>
        <button onClick={() => router.back()} className="absolute top-6 left-6 text-white/50 hover:text-white transition">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="text-center space-y-6 max-w-md">
          <h1 className="text-2xl font-bold text-white">{meditation.title}</h1>
          <p className="text-white/60 text-sm">{meditation.description}</p>
          <p className="text-white/80 text-lg mt-8">How are you feeling right now?</p>
          <div className="flex justify-center gap-3">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                onClick={() => setPreMood(v)}
                className={`flex flex-col items-center gap-1 rounded-xl px-4 py-3 transition-all ${
                  preMood === v
                    ? "bg-teal-500/20 ring-2 ring-teal-400"
                    : "bg-white/5 hover:bg-white/10"
                }`}
              >
                <span className="text-2xl">{["", "😔", "😕", "😐", "🙂", "😊"][v]}</span>
                <span className="text-[11px] text-white/60">{MOOD_LABELS[v]}</span>
              </button>
            ))}
          </div>
          <Button
            onClick={startSession}
            disabled={preMood < 1}
            className="mt-6 bg-teal-500 hover:bg-teal-600 text-white px-8"
          >
            Begin Session
          </Button>
        </div>
      </div>
    );
  }

  // ── Playing ────────────────────────────────────────────────────────────
  if (phase === "playing") {
    const circumference = 2 * Math.PI * 120;
    const strokeOffset = circumference * (1 - progress);

    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-6 pb-8 relative" style={{ background: "#0F1B2D" }}>
        {/* Back button */}
        <button
          onClick={() => { setPlaying(false); setPhase("pre"); setElapsed(0); }}
          className="absolute top-6 left-6 text-white/40 hover:text-white transition"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>

        {/* Timer display */}
        <p className="absolute top-6 right-6 text-white/40 text-sm font-mono">
          {formatTime(elapsed)} / {formatTime(totalSeconds)}
        </p>

        {/* Central area */}
        <div className="relative flex items-center justify-center" style={{ width: 'min(280px, 80vw)', height: 'min(280px, 80vw)' }}>
          {/* Progress ring */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 280 280">
            <circle cx={140} cy={140} r={120} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={4} />
            <circle
              cx={140} cy={140} r={120}
              fill="none"
              stroke="#14B8A6"
              strokeWidth={4}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeOffset}
              transform="rotate(-90 140 140)"
              className="transition-all duration-1000"
            />
          </svg>

          {/* Breathing circle */}
          {hasBreath ? (
            <div
              className="rounded-full animate-breathe"
              style={{
                width: 100,
                height: 100,
                background: "radial-gradient(circle, rgba(20,184,166,0.4) 0%, rgba(20,184,166,0.05) 70%)",
                boxShadow: "0 0 60px rgba(20,184,166,0.2)",
              }}
            />
          ) : (
            <div
              className="rounded-full"
              style={{
                width: 60,
                height: 60,
                background: "radial-gradient(circle, rgba(20,184,166,0.25) 0%, transparent 70%)",
              }}
            />
          )}
        </div>

        {/* Instruction text */}
        <p
          key={stepIdx}
          className="mt-10 text-center text-lg text-white/90 max-w-md leading-relaxed animate-fadeIn"
        >
          {currentStep?.instruction_text}
        </p>

        {hasBreath && (
          <p className="mt-3 text-teal-400/60 text-xs tracking-widest uppercase">Breathe with the circle</p>
        )}

        {/* Controls */}
        <div className="mt-10 flex items-center gap-6">
          <button onClick={skipBack} className="text-white/40 hover:text-white transition">
            <SkipBack className="h-6 w-6" />
          </button>
          <button
            onClick={togglePlay}
            className="flex h-14 w-14 items-center justify-center rounded-full bg-teal-500/20 text-teal-400 hover:bg-teal-500/30 transition"
          >
            {playing ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6 ml-0.5" />}
          </button>
          <button onClick={skipForward} className="text-white/40 hover:text-white transition">
            <SkipForward className="h-6 w-6" />
          </button>
        </div>

        {/* Step indicator */}
        <p className="mt-4 text-white/30 text-xs">
          Step {stepIdx + 1} of {meditation.steps.length}
        </p>

        {/* CSS animations */}
        <style jsx>{`
          @keyframes breathe {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            25% { transform: scale(1.6); opacity: 0.9; }
            50% { transform: scale(1.6); opacity: 0.9; }
            75% { transform: scale(1); opacity: 0.5; }
          }
          .animate-breathe {
            animation: breathe 12s ease-in-out infinite;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fadeIn {
            animation: fadeIn 0.6s ease-out;
          }
        `}</style>
      </div>
    );
  }

  // ── Post-session mood ──────────────────────────────────────────────────
  if (phase === "post") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-6" style={{ background: "#0F1B2D" }}>
        <div className="text-center space-y-6 max-w-md">
          <div className="text-teal-400 text-4xl">✨</div>
          <h2 className="text-2xl font-bold text-white">Session Complete</h2>
          <p className="text-white/60">{meditation.title} — {meditation.duration_minutes} minutes</p>
          <p className="text-white/80 text-lg mt-6">How are you feeling now?</p>
          <div className="flex justify-center gap-3">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                onClick={() => setPostMood(v)}
                className={`flex flex-col items-center gap-1 rounded-xl px-4 py-3 transition-all ${
                  postMood === v
                    ? "bg-teal-500/20 ring-2 ring-teal-400"
                    : "bg-white/5 hover:bg-white/10"
                }`}
              >
                <span className="text-2xl">{["", "😔", "😕", "😐", "🙂", "😊"][v]}</span>
                <span className="text-[11px] text-white/60">{MOOD_LABELS[v]}</span>
              </button>
            ))}
          </div>
          <Button
            onClick={submitPost}
            disabled={postMood < 1}
            className="mt-4 bg-teal-500 hover:bg-teal-600 text-white px-8"
          >
            Submit
          </Button>
        </div>
      </div>
    );
  }

  // ── Done ───────────────────────────────────────────────────────────────
  if (phase === "done") {
    const d = delta ?? 0;
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-6" style={{ background: "#0F1B2D" }}>
        <div className="text-center space-y-6 max-w-md">
          <div className="text-5xl">{d > 0 ? "🌟" : d === 0 ? "🧘" : "💙"}</div>
          <h2 className="text-2xl font-bold text-white">
            {d > 0 ? `You improved by +${d}!` : d === 0 ? "Your mood stayed steady." : "Thank you for showing up."}
          </h2>
          <div className="flex justify-center gap-8 text-sm text-white/50">
            <div>
              <p className="text-white/30">Before</p>
              <p className="text-xl">{["", "😔", "😕", "😐", "🙂", "😊"][preMood]}</p>
            </div>
            <div className="text-2xl text-teal-400 self-end">→</div>
            <div>
              <p className="text-white/30">After</p>
              <p className="text-xl">{["", "😔", "😕", "😐", "🙂", "😊"][postMood]}</p>
            </div>
          </div>
          <div className="flex flex-col items-center gap-3 mt-6">
            <Button onClick={() => router.push("/guidedmeditation")} className="bg-teal-500 hover:bg-teal-600 text-white px-8">
              More Meditations
            </Button>
            <Button variant="ghost" onClick={() => router.push("/dashboard")} className="text-white/50 hover:text-white">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
