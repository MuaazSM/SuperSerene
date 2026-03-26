"use client";

import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, ArrowRight, CheckCircle2, ClipboardList, Shield, Brain, Pill } from "lucide-react";
import { apiClient } from "@/lib/api";

// ── Instrument data (mirrors backend) ────────────────────────────────────

const LIKERT_4 = [
  { value: 0, label: "Not at all" },
  { value: 1, label: "Several days" },
  { value: 2, label: "More than half the days" },
  { value: 3, label: "Nearly every day" },
];

const YES_NO = [
  { value: 0, label: "No" },
  { value: 1, label: "Yes" },
];

type Option = { value: number; label: string };
type Question = { index: number; text: string; options: Option[] };
type Instrument = {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  instructions: string;
  questions: Question[];
};

const INSTRUMENTS: Instrument[] = [
  {
    id: "PHQ_A",
    title: "PHQ-A Depression Screen",
    subtitle: "9 questions — measures depression severity",
    icon: <Brain className="h-5 w-5" />,
    instructions: "Over the past 2 weeks, how often have you been bothered by any of the following problems?",
    questions: [
      "Little interest or pleasure in doing things",
      "Feeling down, depressed, or hopeless",
      "Trouble falling or staying asleep, or sleeping too much",
      "Feeling tired or having little energy",
      "Poor appetite or overeating",
      "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
      "Trouble concentrating on things, such as reading or watching videos",
      "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
      "Thoughts that you would be better off dead, or of hurting yourself in some way",
    ].map((text, i) => ({ index: i, text, options: LIKERT_4 })),
  },
  {
    id: "GAD_7",
    title: "GAD-7 Anxiety Screen",
    subtitle: "7 questions — measures anxiety severity",
    icon: <Shield className="h-5 w-5" />,
    instructions: "Over the past 2 weeks, how often have you been bothered by the following problems?",
    questions: [
      "Feeling nervous, anxious, or on edge",
      "Not being able to stop or control worrying",
      "Worrying too much about different things",
      "Trouble relaxing",
      "Being so restless that it is hard to sit still",
      "Becoming easily annoyed or irritable",
      "Feeling afraid, as if something awful might happen",
    ].map((text, i) => ({ index: i, text, options: LIKERT_4 })),
  },
  {
    id: "CRAFFT",
    title: "CRAFFT Substance Use Screen",
    subtitle: "6 questions — screens for substance use risk",
    icon: <Pill className="h-5 w-5" />,
    instructions: "Please answer Yes or No to each of the following questions.",
    questions: [
      "Have you ever ridden in a CAR driven by someone (including yourself) who was high or had been using alcohol or drugs?",
      "Do you ever use alcohol or drugs to RELAX, feel better about yourself, or fit in?",
      "Do you ever use alcohol or drugs while you are by yourself, or ALONE?",
      "Do you ever FORGET things you did while using alcohol or drugs?",
      "Do your FAMILY or FRIENDS ever tell you that you should cut down on your drinking or drug use?",
      "Have you ever gotten into TROUBLE while you were using alcohol or drugs?",
    ].map((text, i) => ({ index: i, text, options: YES_NO })),
  },
];

// ── Band colours ─────────────────────────────────────────────────────────

const BAND_STYLES: Record<string, string> = {
  green: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40",
  yellow: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40",
  orange: "bg-orange-500/20 text-orange-300 border-orange-500/40",
  red: "bg-red-500/20 text-red-400 border-red-500/40",
};

const BAND_BG: Record<string, string> = {
  green: "from-emerald-500/10 to-transparent",
  yellow: "from-yellow-500/10 to-transparent",
  orange: "from-orange-500/10 to-transparent",
  red: "from-red-500/10 to-transparent",
};

// ── Component ────────────────────────────────────────────────────────────

type ResultData = {
  instrument: string;
  raw_score: number;
  max_score: number;
  severity_label: string;
  severity_band: string;
  care_level: string;
  care_description: string;
  interpretation: string;
};

type CompositeResult = {
  overall_severity_band: string;
  overall_severity_label: string;
  overall_care_level: string;
  overall_care_description: string;
  instruments: ResultData[];
};

type Phase = "select" | "screening" | "results";

export default function ScreeningPage() {
  const [phase, setPhase] = useState<Phase>("select");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [currentInstrIdx, setCurrentInstrIdx] = useState(0);
  const [currentQIdx, setCurrentQIdx] = useState(0);
  // answers[instrumentId][questionIdx] = selected value
  const [answers, setAnswers] = useState<Record<string, (number | null)[]>>({});
  const [results, setResults] = useState<CompositeResult | null>(null);
  const [scoring, setScoring] = useState(false);

  // Derived
  const activeInstruments = useMemo(
    () => INSTRUMENTS.filter((i) => selectedIds.includes(i.id)),
    [selectedIds],
  );
  const currentInstrument = activeInstruments[currentInstrIdx] ?? null;
  const currentQuestion = currentInstrument?.questions[currentQIdx] ?? null;
  const totalQuestions = activeInstruments.reduce((s, i) => s + i.questions.length, 0);
  const answeredSoFar = useMemo(() => {
    let count = 0;
    for (let i = 0; i < currentInstrIdx; i++) {
      count += activeInstruments[i].questions.length;
    }
    count += currentQIdx;
    return count;
  }, [currentInstrIdx, currentQIdx, activeInstruments]);
  const progress = totalQuestions > 0 ? ((answeredSoFar + (answers[currentInstrument?.id ?? ""]?.[currentQIdx] != null ? 1 : 0)) / totalQuestions) * 100 : 0;

  // ── Handlers ───────────────────────────────────────────────────────────

  function toggleInstrument(id: string) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  function selectAll() {
    setSelectedIds(INSTRUMENTS.map((i) => i.id));
  }

  function startScreening() {
    if (selectedIds.length === 0) return;
    const init: Record<string, (number | null)[]> = {};
    for (const inst of activeInstruments) {
      init[inst.id] = Array(inst.questions.length).fill(null);
    }
    setAnswers(init);
    setCurrentInstrIdx(0);
    setCurrentQIdx(0);
    setPhase("screening");
  }

  function selectAnswer(value: number) {
    if (!currentInstrument) return;
    setAnswers((prev) => {
      const copy = { ...prev };
      copy[currentInstrument.id] = [...(copy[currentInstrument.id] ?? [])];
      copy[currentInstrument.id][currentQIdx] = value;
      return copy;
    });
  }

  function goNext() {
    if (!currentInstrument) return;
    if (currentQIdx < currentInstrument.questions.length - 1) {
      setCurrentQIdx((p) => p + 1);
    } else if (currentInstrIdx < activeInstruments.length - 1) {
      setCurrentInstrIdx((p) => p + 1);
      setCurrentQIdx(0);
    } else {
      submitAll();
    }
  }

  function goBack() {
    if (currentQIdx > 0) {
      setCurrentQIdx((p) => p - 1);
    } else if (currentInstrIdx > 0) {
      setCurrentInstrIdx((p) => p - 1);
      setCurrentQIdx(activeInstruments[currentInstrIdx - 1].questions.length - 1);
    }
  }

  async function submitAll() {
    setScoring(true);
    try {
      const payload: Record<string, number[]> = {};
      for (const inst of activeInstruments) {
        payload[inst.id] = (answers[inst.id] ?? []).map((v) => v ?? 0);
      }
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/screening/composite`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
      );
      if (res.ok) {
        const data: CompositeResult = await res.json();
        setResults(data);
      } else {
        // Fallback: score locally
        scoreLocally();
      }
    } catch {
      scoreLocally();
    } finally {
      setScoring(false);
      setPhase("results");
    }
  }

  function scoreLocally() {
    const scored: ResultData[] = [];
    for (const inst of activeInstruments) {
      const ans = (answers[inst.id] ?? []).map((v) => v ?? 0);
      const raw = ans.reduce((a, b) => a + b, 0);
      const max = inst.id === "CRAFFT" ? 6 : inst.id === "GAD_7" ? 21 : 27;
      let band = "green", label = "minimal", care = "self_help";
      if (inst.id === "CRAFFT") {
        band = raw >= 2 ? "orange" : "green";
        label = raw >= 2 ? "positive" : "negative";
        care = raw >= 2 ? "licensed_counselor" : "self_help";
      } else if (inst.id === "GAD_7") {
        if (raw >= 15) { band = "red"; label = "severe"; care = "teletherapy"; }
        else if (raw >= 10) { band = "orange"; label = "moderate"; care = "licensed_counselor"; }
        else if (raw >= 5) { band = "yellow"; label = "mild"; care = "peer_support"; }
      } else {
        if (raw >= 20) { band = "red"; label = "severe"; care = "crisis_line"; }
        else if (raw >= 15) { band = "red"; label = "moderately_severe"; care = "teletherapy"; }
        else if (raw >= 10) { band = "orange"; label = "moderate"; care = "licensed_counselor"; }
        else if (raw >= 5) { band = "yellow"; label = "mild"; care = "peer_support"; }
      }
      scored.push({
        instrument: inst.id,
        raw_score: raw,
        max_score: max,
        severity_label: label,
        severity_band: band,
        care_level: care,
        care_description: "",
        interpretation: `${inst.id.replace("_", "-")} score ${raw}/${max} — ${label.replace("_", " ")}`,
      });
    }
    const bandOrder = { green: 0, yellow: 1, orange: 2, red: 3 };
    const worst = scored.reduce((a, b) => (bandOrder[b.severity_band as keyof typeof bandOrder] ?? 0) > (bandOrder[a.severity_band as keyof typeof bandOrder] ?? 0) ? b : a, scored[0]);
    setResults({
      overall_severity_band: worst.severity_band,
      overall_severity_label: worst.severity_label,
      overall_care_level: worst.care_level,
      overall_care_description: worst.care_description,
      instruments: scored,
    });
  }

  const isLastQuestion =
    currentInstrIdx === activeInstruments.length - 1 &&
    currentQIdx === (currentInstrument?.questions.length ?? 1) - 1;

  const currentAnswer = currentInstrument ? answers[currentInstrument.id]?.[currentQIdx] : null;

  // ── Render ─────────────────────────────────────────────────────────────

  // Phase: Select instruments
  if (phase === "select") {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-2xl space-y-8">
          <div className="text-center space-y-2">
            <ClipboardList className="mx-auto h-10 w-10 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">Mental Health Screening</h1>
            <p className="text-muted-foreground max-w-md mx-auto">
              Clinically validated instruments to help understand your well-being. Your answers are confidential.
            </p>
          </div>

          <div className="grid gap-4">
            {INSTRUMENTS.map((inst) => {
              const selected = selectedIds.includes(inst.id);
              return (
                <Card
                  key={inst.id}
                  className={`cursor-pointer transition-all ${selected ? "border-primary ring-1 ring-primary/50" : "hover:border-muted-foreground/30"}`}
                  onClick={() => toggleInstrument(inst.id)}
                >
                  <CardContent className="flex items-center gap-4 p-5">
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${selected ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                      {inst.icon}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold">{inst.title}</p>
                      <p className="text-sm text-muted-foreground">{inst.subtitle}</p>
                    </div>
                    <div className={`h-5 w-5 rounded-full border-2 transition-colors ${selected ? "border-primary bg-primary" : "border-muted-foreground/30"}`}>
                      {selected && <CheckCircle2 className="h-full w-full text-primary-foreground" />}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="flex items-center justify-center gap-3">
            <Button variant="outline" onClick={selectAll}>
              Full Assessment (All 3)
            </Button>
            <Button onClick={startScreening} disabled={selectedIds.length === 0}>
              Begin Screening <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Phase: Screening questions
  if (phase === "screening" && currentInstrument && currentQuestion) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-4">
        {/* Progress bar */}
        <div className="fixed top-16 left-0 right-0 z-40 px-4">
          <div className="mx-auto max-w-2xl">
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="mt-2 flex justify-between text-xs text-muted-foreground">
              <span>{currentInstrument.title}</span>
              <span>
                {answeredSoFar + 1} / {totalQuestions}
              </span>
            </div>
          </div>
        </div>

        <div className="w-full max-w-2xl space-y-10">
          {/* Instruction */}
          <p className="text-sm text-muted-foreground text-center">{currentInstrument.instructions}</p>

          {/* Question */}
          <h2 className="text-xl font-semibold text-center leading-relaxed">
            {currentQuestion.text}
          </h2>

          {/* Options */}
          <div className="flex flex-col gap-3 max-w-md mx-auto">
            {currentQuestion.options.map((opt) => (
              <Button
                key={opt.value}
                variant={currentAnswer === opt.value ? "default" : "outline"}
                className="justify-start text-left h-auto py-3 px-4"
                onClick={() => selectAnswer(opt.value)}
              >
                <span className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-medium mr-3 ${currentAnswer === opt.value ? "border-primary-foreground bg-primary-foreground/20 text-primary-foreground" : "border-muted-foreground/40"}`}>
                  {opt.value}
                </span>
                {opt.label}
              </Button>
            ))}
          </div>

          {/* Navigation */}
          <div className="flex justify-center gap-4">
            <Button
              variant="ghost"
              onClick={goBack}
              disabled={currentInstrIdx === 0 && currentQIdx === 0}
            >
              <ArrowLeft className="mr-1 h-4 w-4" /> Back
            </Button>
            <Button onClick={goNext} disabled={currentAnswer == null || scoring}>
              {scoring ? "Scoring..." : isLastQuestion ? "Finish & Score" : "Next"}{" "}
              <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Phase: Results
  if (phase === "results" && results) {
    const band = results.overall_severity_band;
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-2xl space-y-8">
          {/* Overall card */}
          <Card className={`bg-gradient-to-b ${BAND_BG[band] ?? ""}`}>
            <CardHeader className="text-center">
              <Badge className={`mx-auto mb-2 px-3 py-1 text-sm border ${BAND_STYLES[band] ?? ""}`}>
                {band.toUpperCase()} — {results.overall_severity_label.replace(/_/g, " ")}
              </Badge>
              <CardTitle className="text-2xl">Your Screening Results</CardTitle>
              <CardDescription>{results.overall_care_description || "See individual results below."}</CardDescription>
            </CardHeader>
          </Card>

          {/* Per-instrument cards */}
          {results.instruments.map((r) => (
            <Card key={r.instrument}>
              <CardContent className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{r.instrument.replace(/_/g, "-")}</span>
                  <Badge className={`border ${BAND_STYLES[r.severity_band] ?? ""}`}>
                    {r.severity_band.toUpperCase()}
                  </Badge>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-3xl font-bold">{r.raw_score}</div>
                  <span className="text-muted-foreground">/ {r.max_score}</span>
                </div>
                <p className="text-sm text-muted-foreground">{r.interpretation}</p>
                {/* Score bar */}
                <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full rounded-full transition-all ${r.severity_band === "green" ? "bg-emerald-500" : r.severity_band === "yellow" ? "bg-yellow-500" : r.severity_band === "orange" ? "bg-orange-500" : "bg-red-500"}`}
                    style={{ width: `${(r.raw_score / r.max_score) * 100}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Actions */}
          <div className="flex flex-col items-center gap-3">
            <Button asChild className="w-full max-w-xs">
              <a href={band === "red" ? "/psychologist-consultation" : band === "orange" ? "/psychologist-consultation" : "/exercise"}>
                View Recommended Next Steps
              </a>
            </Button>
            <Button variant="outline" onClick={() => { setPhase("select"); setResults(null); setSelectedIds([]); }}>
              Retake Screening
            </Button>
            <Button variant="ghost" asChild>
              <a href="/dashboard">Return to Dashboard</a>
            </Button>
          </div>

          {/* Disclaimer */}
          <p className="text-center text-xs text-muted-foreground max-w-md mx-auto">
            This screening is not a diagnosis. Results are based on validated clinical instruments (PHQ-A, GAD-7, CRAFFT) and should be reviewed with a qualified healthcare provider.
          </p>
        </div>
      </div>
    );
  }

  return null;
}
