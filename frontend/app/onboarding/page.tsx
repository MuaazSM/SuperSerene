'use client'
import React, { useState } from 'react'
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";
import { Button } from '@/components/ui/button';
import { ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

// ── PHQ-A screening (primary) ────────────────────────────────────────────

const PHQ_A_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
    "Trouble concentrating on things, such as reading or watching videos",
    "Moving or speaking so slowly that other people could have noticed? Or being so fidgety or restless that you have been moving around a lot more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself in some way",
];

const PHQ_OPTIONS = [
    { value: 0, label: "Not at all" },
    { value: 1, label: "Several days" },
    { value: 2, label: "More than half the days" },
    { value: 3, label: "Nearly every day" },
];

// ── EQ Likert (optional secondary) ───────────────────────────────────────

const EQ_QUESTIONS = [
    "How often do you take time to reflect on your emotions and understand why you feel a certain way?",
    "How often do you recognize and understand the feelings of others in different situations?",
    "How often are you able to stay calm and manage your emotions during stressful or challenging situations?",
    "How often do you communicate your feelings clearly and respectfully to others?",
    "How often do you stay motivated and positive, even when faced with setbacks?",
    "How often do you bounce back quickly after experiencing disappointment or failure?",
];

const EQ_OPTIONS = [
    { value: 0, label: "Rarely", score: 0 },
    { value: 1, label: "Sometimes", score: 0.2 },
    { value: 2, label: "Often", score: 0.4 },
    { value: 3, label: "Very Often", score: 0.6 },
    { value: 4, label: "Always", score: 0.8 },
];

const FOCUS_OPTIONS = [
    { value: 0, label: "Self Awareness" },
    { value: 1, label: "Self Regulation" },
    { value: 2, label: "Motivation" },
    { value: 3, label: "Empathy" },
    { value: 4, label: "Social Skills" },
];

// ── Severity scoring (mirrors backend) ───────────────────────────────────

function scorePHQ(answers: number[]): { raw: number; band: string; label: string; care: string } {
    const raw = answers.reduce((a, b) => a + b, 0);
    if (raw >= 20) return { raw, band: "red", label: "severe", care: "crisis_line" };
    if (raw >= 15) return { raw, band: "red", label: "moderately severe", care: "teletherapy" };
    if (raw >= 10) return { raw, band: "orange", label: "moderate", care: "licensed_counselor" };
    if (raw >= 5) return { raw, band: "yellow", label: "mild", care: "peer_support" };
    return { raw, band: "green", label: "minimal", care: "self_help" };
}

const BAND_STYLES: Record<string, string> = {
    green: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40",
    yellow: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40",
    orange: "bg-orange-500/20 text-orange-300 border-orange-500/40",
    red: "bg-red-500/20 text-red-400 border-red-500/40",
};

// ── Component ────────────────────────────────────────────────────────────

type Phase = "phq" | "eq_prompt" | "eq" | "focus" | "results";

export default function Onboarding() {
    const [phase, setPhase] = useState<Phase>("phq");
    const [phqIdx, setPhqIdx] = useState(0);
    const [phqAnswers, setPhqAnswers] = useState<(number | null)[]>(Array(PHQ_A_QUESTIONS.length).fill(null));

    const [eqIdx, setEqIdx] = useState(0);
    const [eqAnswers, setEqAnswers] = useState<(number | null)[]>(Array(EQ_QUESTIONS.length).fill(null));
    const [focusChoice, setFocusChoice] = useState<number | null>(null);

    const [result, setResult] = useState<{ raw: number; band: string; label: string; care: string } | null>(null);

    // Total progress
    const phqTotal = PHQ_A_QUESTIONS.length;
    const progress =
        phase === "phq"
            ? ((phqIdx + (phqAnswers[phqIdx] != null ? 1 : 0)) / phqTotal) * 100
            : 100;

    // ── PHQ handlers ─────────────────────────────────────────────────────

    function selectPhq(value: number) {
        setPhqAnswers((prev) => {
            const copy = [...prev];
            copy[phqIdx] = value;
            return copy;
        });
    }

    function nextPhq() {
        if (phqIdx < phqTotal - 1) {
            setPhqIdx((p) => p + 1);
        } else {
            // Score and submit
            const answers = phqAnswers.map((v) => v ?? 0);
            const scored = scorePHQ(answers);
            setResult(scored);

            // Persist
            localStorage.setItem("phq_score", JSON.stringify(scored));
            localStorage.setItem("phq_answers", JSON.stringify(answers));

            // Try backend
            fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/screening/PHQ_A/score`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ answers }),
            }).catch(() => { /* offline ok */ });

            setPhase("eq_prompt");
        }
    }

    function backPhq() {
        if (phqIdx > 0) setPhqIdx((p) => p - 1);
    }

    // ── EQ handlers ──────────────────────────────────────────────────────

    function selectEq(value: number) {
        setEqAnswers((prev) => {
            const copy = [...prev];
            copy[eqIdx] = value;
            return copy;
        });
    }

    function nextEq() {
        if (eqIdx < EQ_QUESTIONS.length - 1) {
            setEqIdx((p) => p + 1);
        } else {
            setPhase("focus");
        }
    }

    function backEq() {
        if (eqIdx > 0) setEqIdx((p) => p - 1);
        else setPhase("eq_prompt");
    }

    // ── Finish ───────────────────────────────────────────────────────────

    function finish() {
        // Store EQ score
        const eqScore = eqAnswers.reduce((acc, val) => acc + (val != null ? EQ_OPTIONS[val]?.score ?? 0 : 0), 0);
        localStorage.setItem("onboardingScore", eqScore.toString());
        if (focusChoice != null) {
            localStorage.setItem("focusArea", FOCUS_OPTIONS[focusChoice].label);
        }
        setPhase("results");
    }

    function skipToResults() {
        // Store default EQ score
        localStorage.setItem("onboardingScore", "0");
        setPhase("results");
    }

    function goToDashboard() {
        window.location.href = "/dashboard";
    }

    // ── Render ───────────────────────────────────────────────────────────

    // PHQ-A screening
    if (phase === "phq") {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
                {/* Progress */}
                <div className="fixed top-16 left-0 right-0 z-40 px-4">
                    <div className="mx-auto max-w-2xl">
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                            <div className="h-full rounded-full bg-primary transition-all duration-300" style={{ width: `${progress}%` }} />
                        </div>
                        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                            <span>PHQ-A Depression Screening</span>
                            <span>{phqIdx + 1} / {phqTotal}</span>
                        </div>
                    </div>
                </div>

                <div className="w-full max-w-2xl space-y-8 text-center">
                    <p className="text-sm text-muted-foreground">Over the past 2 weeks, how often have you been bothered by this problem?</p>

                    <div className="text-lg sm:text-xl md:text-2xl">
                        <TextGenerateEffect
                            key={`phq-${phqIdx}`}
                            words={PHQ_A_QUESTIONS[phqIdx]}
                        />
                    </div>

                    <div className="flex flex-col gap-3 max-w-md mx-auto">
                        {PHQ_OPTIONS.map((opt) => (
                            <Button
                                key={opt.value}
                                variant={phqAnswers[phqIdx] === opt.value ? "default" : "outline"}
                                className="justify-start text-left h-auto min-h-[44px] py-3 px-4"
                                onClick={() => selectPhq(opt.value)}
                            >
                                <span className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-medium mr-3 ${phqAnswers[phqIdx] === opt.value ? "border-primary-foreground bg-primary-foreground/20 text-primary-foreground" : "border-muted-foreground/40"}`}>
                                    {opt.value}
                                </span>
                                {opt.label}
                            </Button>
                        ))}
                    </div>

                    <div className="flex justify-center gap-4">
                        <Button variant="ghost" onClick={backPhq} disabled={phqIdx === 0}>
                            <ArrowLeft className="mr-1 h-4 w-4" /> Back
                        </Button>
                        <Button onClick={nextPhq} disabled={phqAnswers[phqIdx] == null}>
                            {phqIdx === phqTotal - 1 ? "Score" : "Next"} <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // Prompt to take optional EQ assessment
    if (phase === "eq_prompt" && result) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
                <div className="w-full max-w-lg space-y-6 text-center">
                    <Badge className={`px-3 py-1 text-sm border ${BAND_STYLES[result.band]}`}>
                        {result.band.toUpperCase()} — {result.label}
                    </Badge>
                    <h2 className="text-2xl font-bold">PHQ-A Score: {result.raw}/27</h2>
                    <p className="text-muted-foreground">
                        Great job completing the screening. Would you also like to take a quick emotional intelligence assessment? This helps us personalize your experience.
                    </p>
                    <div className="flex flex-col items-center gap-3">
                        <Button onClick={() => setPhase("eq")} className="w-full max-w-xs">
                            Yes, take EQ assessment <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                        <Button variant="ghost" onClick={skipToResults}>
                            Skip for now
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // EQ Likert questions
    if (phase === "eq") {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
                <div className="fixed top-16 left-0 right-0 z-40 px-4">
                    <div className="mx-auto max-w-2xl">
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                            <div className="h-full rounded-full bg-primary/60 transition-all duration-300" style={{ width: `${((eqIdx + 1) / EQ_QUESTIONS.length) * 100}%` }} />
                        </div>
                        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                            <span>Emotional Intelligence Assessment (optional)</span>
                            <span>{eqIdx + 1} / {EQ_QUESTIONS.length}</span>
                        </div>
                    </div>
                </div>

                <div className="w-full max-w-2xl space-y-8 text-center">
                    <TextGenerateEffect key={`eq-${eqIdx}`} words={EQ_QUESTIONS[eqIdx]} />
                    <div className="flex justify-center gap-3 flex-wrap">
                        {EQ_OPTIONS.map((opt) => (
                            <Button
                                key={opt.value}
                                variant={eqAnswers[eqIdx] === opt.value ? "default" : "ghost"}
                                onClick={() => selectEq(opt.value)}
                            >
                                {opt.label}
                            </Button>
                        ))}
                    </div>
                    <div className="flex justify-center gap-4">
                        <Button variant="ghost" onClick={backEq}>
                            <ArrowLeft className="mr-1 h-4 w-4" /> Back
                        </Button>
                        <Button onClick={nextEq} disabled={eqAnswers[eqIdx] == null}>
                            {eqIdx === EQ_QUESTIONS.length - 1 ? "Next" : "Next"} <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // Focus area selection
    if (phase === "focus") {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
                <div className="w-full max-w-2xl space-y-8 text-center">
                    <TextGenerateEffect key="focus" words="What area do you want to focus on first?" />
                    <div className="flex justify-center gap-3 flex-wrap">
                        {FOCUS_OPTIONS.map((opt) => (
                            <Button
                                key={opt.value}
                                variant={focusChoice === opt.value ? "default" : "ghost"}
                                onClick={() => setFocusChoice(opt.value)}
                            >
                                {opt.label}
                            </Button>
                        ))}
                    </div>
                    <div className="flex justify-center gap-4">
                        <Button variant="ghost" onClick={() => setPhase("eq")}>
                            <ArrowLeft className="mr-1 h-4 w-4" /> Back
                        </Button>
                        <Button onClick={finish} disabled={focusChoice == null}>
                            Finish <CheckCircle2 className="ml-1 h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // Results
    if (phase === "results" && result) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen p-4">
                <div className="w-full max-w-lg space-y-6 text-center">
                    <CheckCircle2 className="mx-auto h-12 w-12 text-primary" />
                    <h1 className="text-3xl font-bold">You&apos;re all set!</h1>
                    <Badge className={`px-3 py-1 text-sm border ${BAND_STYLES[result.band]}`}>
                        PHQ-A: {result.raw}/27 — {result.label}
                    </Badge>
                    <p className="text-muted-foreground">
                        Your personalized dashboard is ready. We&apos;ll use your results to tailor exercises, check-ins, and support to your needs.
                    </p>
                    <Button onClick={goToDashboard} className="w-full max-w-xs">
                        Go to Dashboard <ArrowRight className="ml-1 h-4 w-4" />
                    </Button>
                    <Button variant="ghost" asChild>
                        <a href="/screening">Take Full Assessment (GAD-7 + CRAFFT)</a>
                    </Button>
                </div>
            </div>
        );
    }

    return null;
}
