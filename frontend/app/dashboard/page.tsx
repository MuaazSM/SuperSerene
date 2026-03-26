"use client";

import { useEffect, useState } from "react"
import { IconArrowUpRight, IconCalendarTime, IconFlame, IconSparkles, IconTargetArrow, IconAlertTriangle } from "@tabler/icons-react"
import Link from "next/link"

import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { SectionCards } from "@/components/section-cards"
import { Badge } from "@/components/ui/badge"
import {
    Card,
    CardContent,
    CardDescription,
    CardAction,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

const focusActions = [
    {
        title: "Daily grounding",
        detail: "3 minute breath scan to reset",
        cta: "Start exercise",
    },
    {
        title: "Reframe a thought",
        detail: "Pick one worry and rewrite it",
        cta: "Open journal",
    },
    {
        title: "Micro-connection",
        detail: "Send one supportive message",
        cta: "View prompts",
    },
]

const upcomingMoments = [
    { label: "Next check-in", time: "Today, 5:00 PM", accent: "primary" },
    { label: "Reflection window", time: "Tomorrow, 8:00 AM", accent: "accent" },
    { label: "Stretch goal", time: "This week", accent: "secondary" },
]

export default function Page() {
    const [showBanner, setShowBanner] = useState(false)
    const [showMeditationSuggestion, setShowMeditationSuggestion] = useState(false)

    useEffect(() => {
        try {
            const stored = localStorage.getItem("phq_score")
            if (stored) {
                const parsed = JSON.parse(stored)
                const band = parsed?.band
                if (band === "orange" || band === "red") {
                    setShowBanner(true)
                } else if (band === "green" || band === "yellow") {
                    setShowMeditationSuggestion(true)
                }
            }
        } catch { /* */ }
    }, [])

    return (
        <div className="relative isolate flex flex-1 flex-col overflow-hidden bg-gradient-to-b from-slate-50 via-white to-white dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 overflow-y-hidden">
            <div className="pointer-events-none absolute inset-x-0 top-[-10%] h-64 bg-gradient-to-r from-indigo-200/40 via-sky-200/30 to-emerald-200/30 blur-3xl dark:from-indigo-500/10 dark:via-sky-400/5 dark:to-emerald-400/10" />

            <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-4 pb-12 pt-8 lg:px-8 lg:pt-10">
                {showBanner && (
                    <div className="mb-6 flex items-center gap-3 rounded-xl border border-orange-500/30 bg-orange-500/10 px-5 py-3 text-sm">
                        <IconAlertTriangle className="h-5 w-5 shrink-0 text-orange-400" />
                        <span className="flex-1 text-orange-200">
                            Based on your assessment, we recommend speaking with a professional.
                        </span>
                        <Link
                            href="/teletherapy"
                            className="shrink-0 rounded-lg bg-orange-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-orange-600 transition-colors"
                        >
                            Find a counselor &rarr;
                        </Link>
                    </div>
                )}
                {showMeditationSuggestion && !showBanner && (
                    <div className="mb-6 flex items-center gap-3 rounded-xl border border-teal-500/30 bg-teal-500/10 px-5 py-3 text-sm">
                        <IconSparkles className="h-5 w-5 shrink-0 text-teal-400" />
                        <span className="flex-1 text-teal-200">
                            Your mood is steady. Try a quick meditation to maintain it.
                        </span>
                        <Link
                            href="/guidedmeditation/quick_calm"
                            className="shrink-0 rounded-lg bg-teal-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-teal-600 transition-colors"
                        >
                            5-min Quick Calm &rarr;
                        </Link>
                    </div>
                )}
                <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                    <div className="flex flex-col gap-3">
                        <Badge variant="outline" className="w-fit border-primary/30 bg-primary/5 text-primary dark:border-primary/40 dark:bg-primary/10">
                            <IconSparkles className="mr-1.5 size-4" />
                            Welcome back
                        </Badge>
                        <div>
                            <h1 className="text-balance text-3xl font-semibold leading-tight tracking-tight text-slate-900 dark:text-slate-50 lg:text-4xl">
                                Your emotional fitness cockpit
                            </h1>
                            <p className="mt-2 max-w-2xl text-base text-muted-foreground">
                                Track progress, act on the moments that matter, and keep your streak alive with a calm, confident rhythm.
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row w-full sm:w-auto flex-wrap gap-3">
                            <Button size="lg" className="shadow-md shadow-primary/20">
                                <IconTargetArrow className="size-4" />
                                Start guided session
                                <IconArrowUpRight className="size-4" />
                            </Button>
                            <Button size="lg" variant="outline" className="border-dashed">
                                <IconCalendarTime className="size-4" />
                                Plan today
                            </Button>
                        </div>
                    </div>

                    <Card className="relative overflow-hidden w-full lg:max-w-sm">
                        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-emerald-200/20 dark:from-primary/15 dark:to-emerald-400/10" />
                        <CardHeader className="relative">
                            <CardDescription>Consistency streak</CardDescription>
                            <CardTitle className="text-3xl font-semibold">12 days</CardTitle>
                            <CardAction>
                                <Badge variant="outline" className="bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">
                                    <IconFlame className="mr-1 size-4" />
                                    +3 this week
                                </Badge>
                            </CardAction>
                        </CardHeader>
                        <CardContent className="relative">
                            <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-muted">
                                <div className="h-full w-[72%] rounded-full bg-gradient-to-r from-primary to-emerald-400" />
                            </div>
                            <div className="grid grid-cols-3 gap-3 text-sm text-muted-foreground">
                                {upcomingMoments.map((item) => (
                                    <div key={item.label} className="rounded-lg border border-border/70 bg-background/60 p-3 shadow-xs">
                                        <p className="text-xs font-medium text-slate-500 dark:text-slate-300">{item.label}</p>
                                        <p className="mt-1 text-slate-900 dark:text-slate-100">{item.time}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="mt-8 flex flex-col gap-6">
                    <SectionCards />

                    <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
                        <ChartAreaInteractive />

                        <Card className="@container/card h-full">
                            <CardHeader className="pb-4">
                                <CardDescription>Today&apos;s focus</CardDescription>
                                <CardTitle className="text-2xl">3 simple wins</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {focusActions.map((action, idx) => (
                                    <div
                                        key={action.title}
                                        className="rounded-xl border border-dashed border-border/70 bg-card/80 p-4 shadow-xs transition hover:border-primary/50 hover:shadow-sm"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="text-sm font-medium text-slate-900 dark:text-slate-50">
                                                    {action.title}
                                                </p>
                                                <p className="text-sm text-muted-foreground">{action.detail}</p>
                                            </div>
                                            <Badge variant="outline" className="bg-primary/5 text-primary">
                                                Step {idx + 1}
                                            </Badge>
                                        </div>
                                        <Button variant="ghost" size="sm" className="mt-3 px-0 text-primary">
                                            {action.cta}
                                            <IconArrowUpRight className="ml-1 size-4" />
                                        </Button>
                                    </div>
                                ))}
                            </CardContent>
                            <CardFooter className="flex-col items-start gap-3 border-t pt-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2 text-slate-900 dark:text-slate-100">
                                    <IconSparkles className="size-4" />
                                    Micro actions compound over time. Keep the pace light and repeatable.
                                </div>
                                <Separator className="bg-border/70" />
                                <div className="flex w-full items-center justify-between text-xs">
                                    <span>Updated just now</span>
                                    <Button variant="ghost" size="sm" className="h-8 px-2">Save plan</Button>
                                </div>
                            </CardFooter>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
