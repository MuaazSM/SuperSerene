"use client";

import React, { useMemo, useState } from "react";
import { BackgroundBeams } from "@/components/ui/BackgroundBeams";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    IconArrowUp,
    IconArrowDown,
    IconMessageCircle,
    IconShare,
    IconBookmark,
    IconHash,
    IconLoader2,
} from "@tabler/icons-react";

type Topic = {
    id: string;
    name: string;
    description?: string;
};

type Post = {
    id: string;
    topicId: string;
    title: string;
    body: string;
    author: string;
    createdAt: string; // ISO
    votes: number;
    comments: number;
};

const topics: Topic[] = [
    { id: "mindfulness", name: "Mindfulness", description: "Breath, focus, and presence." },
    { id: "relationships", name: "Relationships", description: "Connection, communication, and care." },
    { id: "stress", name: "Stress", description: "Coping and resilience." },
    { id: "sleep", name: "Sleep", description: "Rest and recovery." },
    { id: "growth", name: "Personal Growth", description: "Habits and goals." },
];

const seedPosts: Post[] = [
    // Mindfulness
    {
        id: "p1",
        topicId: "mindfulness",
        title: "3-minute breath reset that actually helps",
        body: "I’ve been using a simple 3-3-3 pattern when overwhelmed. Inhale 3, hold 3, exhale 3 — repeat x5. Works surprisingly well before meetings.",
        author: "alex",
        createdAt: new Date().toISOString(),
        votes: 42,
        comments: 12,
    },
    {
        id: "p1b",
        topicId: "mindfulness",
        title: "Grounding in 60 seconds",
        body: "Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste. Rapid reset for scattered focus.",
        author: "nina",
        createdAt: new Date(Date.now() - 2 * 3600_000).toISOString(),
        votes: 31,
        comments: 9,
    },
    {
        id: "p1c",
        topicId: "mindfulness",
        title: "A mindful commute routine",
        body: "No music for first 5 mins, just breath and posture check. Arrive calmer without extra time.",
        author: "ben",
        createdAt: new Date(Date.now() - 2 * 86400000).toISOString(),
        votes: 24,
        comments: 6,
    },

    // Relationships
    {
        id: "p2",
        topicId: "relationships",
        title: "One sentence that defuses tension",
        body: "When things get heated, I’ve tried: ‘Help me understand your view.’ It changes my tone and keeps us curious, not combative.",
        author: "maya",
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        votes: 67,
        comments: 25,
    },
    {
        id: "p2b",
        topicId: "relationships",
        title: "The 2-minute repair",
        body: "If I snap, I say: ‘I’m sorry. I was stressed. You matter.’ Short, sincere repairs prevent residue.",
        author: "sam",
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
        votes: 38,
        comments: 11,
    },
    {
        id: "p2c",
        topicId: "relationships",
        title: "Weekly check-in prompt",
        body: "Ask: ‘What’s one small thing I can do that would help your week?’ Yields practical, caring actions.",
        author: "rachel",
        createdAt: new Date(Date.now() - 5 * 86400000).toISOString(),
        votes: 29,
        comments: 8,
    },

    // Stress
    {
        id: "p3",
        topicId: "stress",
        title: "Tiny boundaries that protect your energy",
        body: "Saying ‘I’ll get back to you in an hour’ gives me room to think. Small boundary, huge impact on stress.",
        author: "jamal",
        createdAt: new Date(Date.now() - 2 * 86400000).toISOString(),
        votes: 28,
        comments: 7,
    },
    {
        id: "p3b",
        topicId: "stress",
        title: "The 30-30 buffer",
        body: "No meetings within 30 minutes of waking or last 30 of the day. Better nervous system regulation.",
        author: "lee",
        createdAt: new Date(Date.now() - 4 * 86400000).toISOString(),
        votes: 33,
        comments: 10,
    },
    {
        id: "p3c",
        topicId: "stress",
        title: "Anxiety note card",
        body: "I keep a note: ‘It’s okay to feel this. I can take one small step.’ Helps me re-center.",
        author: "tanya",
        createdAt: new Date(Date.now() - 6 * 86400000).toISOString(),
        votes: 22,
        comments: 5,
    },

    // Sleep
    {
        id: "p4",
        topicId: "sleep",
        title: "Blue light blockers: placebo or useful?",
        body: "Tried blockers for a week; subjective improvement. Biggest win was no scrolling after 9pm though.",
        author: "sophia",
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
        votes: 19,
        comments: 6,
    },
    {
        id: "p4b",
        topicId: "sleep",
        title: "Pre-sleep wind-down playlist",
        body: "10 minutes of instrumental, no lyrics. Pairs with dim lights; my sleep latency dropped.",
        author: "amir",
        createdAt: new Date(Date.now() - 7 * 86400000).toISOString(),
        votes: 27,
        comments: 9,
    },
    {
        id: "p4c",
        topicId: "sleep",
        title: "‘Parking lot’ journaling",
        body: "Write tomorrow’s 3 tasks before bed; brain stops looping. Sleep is quieter.",
        author: "jules",
        createdAt: new Date(Date.now() - 9 * 86400000).toISOString(),
        votes: 34,
        comments: 13,
    },

    // Personal Growth
    {
        id: "p5",
        topicId: "growth",
        title: "Two-minute daily habit that stuck",
        body: "I write the next day’s single focus on a sticky note. Micro commitment; macro clarity.",
        author: "li",
        createdAt: new Date(Date.now() - 6 * 86400000).toISOString(),
        votes: 51,
        comments: 14,
    },
    {
        id: "p5b",
        topicId: "growth",
        title: "The ‘minimum viable win’",
        body: "Define the smallest version of progress. Keeps me moving even on low-energy days.",
        author: "drew",
        createdAt: new Date(Date.now() - 10 * 86400000).toISOString(),
        votes: 36,
        comments: 12,
    },
    {
        id: "p5c",
        topicId: "growth",
        title: "Accountability without shame",
        body: "Weekly text with a friend: one win, one wobble, one next step. Motivating, not punitive.",
        author: "keira",
        createdAt: new Date(Date.now() - 12 * 86400000).toISOString(),
        votes: 41,
        comments: 18,
    },
];

export default function CommunityTopics() {
    const [selectedTopic, setSelectedTopic] = useState<string>("mindfulness");
    const [posts, setPosts] = useState<Post[] | null>(null);
    const [sort, setSort] = useState<"top" | "new" | "rising">("top");
    const [query, setQuery] = useState("");
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [newPost, setNewPost] = useState<Pick<Post, "title" | "body" | "author" | "topicId">>({
        title: "",
        body: "",
        author: "you",
        topicId: selectedTopic,
    });
    const [isPosting, setIsPosting] = useState(false);

    const STORAGE_KEY = "community-wellness:posts";

    // Hydrate from localStorage on mount
    React.useEffect(() => {
        try {
            const raw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
            if (raw) {
                const parsed: Post[] = JSON.parse(raw);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    setPosts(parsed);
                    return;
                }
            }
        } catch {
            // ignore parse errors
        }
        // No stored data or parse failed — use seed posts
        setPosts(seedPosts);
    }, []);

    // Persist to localStorage when posts change (skip null = not yet loaded)
    React.useEffect(() => {
        if (posts === null) return;
        try {
            if (typeof window !== "undefined") {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(posts));
            }
        } catch {
            // ignore storage errors
        }
    }, [posts]);

    // Keep newPost topic in sync with selectedTopic when opening
    React.useEffect(() => {
        setNewPost((prev) => ({ ...prev, topicId: selectedTopic }));
    }, [selectedTopic]);

    const filtered = useMemo(() => {
        if (!posts) return [];
        let next = posts.filter((p) => p.topicId === selectedTopic);
        if (query.trim()) {
            const q = query.trim().toLowerCase();
            next = next.filter(
                (p) =>
                    p.title.toLowerCase().includes(q) ||
                    p.body.toLowerCase().includes(q) ||
                    p.author.toLowerCase().includes(q)
            );
        }
        if (sort === "top") next = next.sort((a, b) => b.votes - a.votes);
        if (sort === "new") next = next.sort(
            (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );
        if (sort === "rising") next = next.sort((a, b) => b.comments - a.comments);
        return next;
    }, [posts, selectedTopic, sort, query]);

    const vote = (id: string, delta: 1 | -1) => {
        setPosts((prev) => (prev ?? []).map((p) => (p.id === id ? { ...p, votes: p.votes + delta } : p)));
    };

    const handleCreatePost = () => {
        const title = newPost.title.trim();
        const body = newPost.body.trim();
        if (!title || !body) return;
        setIsPosting(true);
        const delay = 1200 + Math.floor(Math.random() * 900); // ~1.2s–2.1s
        setTimeout(() => {
            const item: Post = {
                id: `local-${Date.now()}`,
                topicId: newPost.topicId,
                title,
                body,
                author: newPost.author || "you",
                createdAt: new Date().toISOString(),
                votes: 0,
                comments: 0,
            };
            setPosts((prev) => [item, ...(prev ?? [])]);
            setIsPosting(false);
            setIsCreateOpen(false);
            setNewPost({ title: "", body: "", author: "you", topicId: selectedTopic });
        }, delay);
    };

    return (
        <div className="relative w-full min-h-screen pt-16 pb-12">
            <div className="relative z-10 mx-auto w-full max-w-7xl px-4">
                <div className="mb-8 flex flex-col gap-2">
                    <Badge variant="outline" className="w-fit border-primary/30 bg-primary/5 text-primary">
                        <IconHash className="mr-1 size-4" /> Topics
                    </Badge>
                    <h1 className="text-3xl font-semibold tracking-tight">Community Wellness</h1>
                    <p className="text-muted-foreground">Browse focused topics and share practical, lived wisdom. Reddit-like, but calmer.</p>
                </div>

                <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
                    {/* Sidebar Topics */}
                    <Card className="h-fit">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-lg">Topics</CardTitle>
                            <CardDescription>Pick a lane, dive in.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {topics.map((t) => (
                                <Button
                                    key={t.id}
                                    variant={selectedTopic === t.id ? "default" : "ghost"}
                                    className="w-full justify-start"
                                    onClick={() => setSelectedTopic(t.id)}
                                >
                                    <span className="mr-2 inline-flex h-2 w-2 rounded-full bg-primary" />
                                    {t.name}
                                </Button>
                            ))}
                        </CardContent>
                        <CardFooter className="flex-col items-start gap-3 border-t pt-4 text-xs text-muted-foreground">
                            <p className="leading-relaxed">Can’t find a topic? Suggest one and we’ll add it.</p>
                            <Button variant="outline" size="sm">Suggest topic</Button>
                        </CardFooter>
                    </Card>

                    {/* Main Content */}
                    <div className="flex flex-col gap-4">
                        <Card>
                            <CardHeader className="pb-3">
                                <CardTitle className="text-xl">{topics.find((t) => t.id === selectedTopic)?.name}</CardTitle>
                                <CardDescription>{topics.find((t) => t.id === selectedTopic)?.description}</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant={sort === "top" ? "default" : "outline"}
                                            size="sm"
                                            onClick={() => setSort("top")}
                                        >Top</Button>
                                        <Button
                                            variant={sort === "new" ? "default" : "outline"}
                                            size="sm"
                                            onClick={() => setSort("new")}
                                        >New</Button>
                                        <Button
                                            variant={sort === "rising" ? "default" : "outline"}
                                            size="sm"
                                            onClick={() => setSort("rising")}
                                        >Rising</Button>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Input
                                            value={query}
                                            onChange={(e) => setQuery(e.target.value)}
                                            placeholder="Search posts"
                                            className="w-full sm:w-64"
                                        />
                                        <Button size="sm" onClick={() => setIsCreateOpen(true)}>Create post</Button>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <div className="space-y-4">
                            {filtered.map((post) => (
                                <Card key={post.id} className="">
                                    <CardContent className="flex gap-4 px-4 py-6">
                                        {/* Votes column */}
                                        <div className="flex w-12 flex-col items-center justify-start rounded-md border bg-background/60 py-2">
                                            <Button variant="ghost" size="icon" onClick={() => vote(post.id, 1)} aria-label="Upvote">
                                                <IconArrowUp className="size-5" />
                                            </Button>
                                            <div className="text-sm font-semibold">{post.votes}</div>
                                            <Button variant="ghost" size="icon" onClick={() => vote(post.id, -1)} aria-label="Downvote">
                                                <IconArrowDown className="size-5" />
                                            </Button>
                                        </div>

                                        {/* Post content */}
                                        <div className="flex-1">
                                            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                                                <Badge variant="outline" className="px-2 py-0 text-[11px]">
                                                    {topics.find((t) => t.id === post.topicId)?.name}
                                                </Badge>
                                                <span>•</span>
                                                <span>by {post.author}</span>
                                                <span>•</span>
                                                <span>{new Date(post.createdAt).toLocaleDateString()}</span>
                                            </div>
                                            <h3 className="mt-1 text-lg font-semibold">{post.title}</h3>
                                            <p className="mt-1 text-sm text-muted-foreground">{post.body}</p>

                                            <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
                                                <Button variant="ghost" size="sm" className="gap-1 px-2">
                                                    <IconMessageCircle className="size-4" /> {post.comments} Comments
                                                </Button>
                                                <Button variant="ghost" size="sm" className="gap-1 px-2">
                                                    <IconShare className="size-4" /> Share
                                                </Button>
                                                <Button variant="ghost" size="sm" className="gap-1 px-2">
                                                    <IconBookmark className="size-4" /> Save
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                            {filtered.length === 0 && (
                                <Card>
                                    <CardContent className="px-6 py-8 text-center text-sm text-muted-foreground">
                                        No posts yet. Be the first to share a practical tip in this topic.
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <BackgroundBeams className="absolute left-0 top-0 -z-10 h-full w-full pointer-events-none" />

            {isCreateOpen && (
                <div className="fixed inset-0 z-50 grid place-items-center">
                    <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setIsCreateOpen(false)} />
                    <Card className="relative z-10 w-full max-w-lg">
                        <CardHeader>
                            <CardTitle>Create a post</CardTitle>
                            <CardDescription>Share a practical tip or experience in a topic.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <label className="text-sm text-muted-foreground">Topic</label>
                                <Select value={newPost.topicId} onValueChange={(v) => setNewPost((p) => ({ ...p, topicId: v }))}>
                                    <SelectTrigger className="w-full" disabled={isPosting}>
                                        <SelectValue placeholder="Select topic" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {topics.map((t) => (
                                            <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm text-muted-foreground">Title</label>
                                <Input
                                    value={newPost.title}
                                    onChange={(e) => setNewPost((p) => ({ ...p, title: e.target.value }))}
                                    placeholder="What’s your tip or insight?"
                                    disabled={isPosting}
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm text-muted-foreground">Body</label>
                                <Textarea
                                    value={newPost.body}
                                    onChange={(e) => setNewPost((p) => ({ ...p, body: e.target.value }))}
                                    placeholder="Share details that help others apply it."
                                    rows={6}
                                    disabled={isPosting}
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm text-muted-foreground">Author</label>
                                <Input
                                    value={newPost.author}
                                    onChange={(e) => setNewPost((p) => ({ ...p, author: e.target.value }))}
                                    placeholder="Your name or alias"
                                    disabled={isPosting}
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="flex items-center justify-end gap-2">
                            <Button variant="ghost" onClick={() => setIsCreateOpen(false)} disabled={isPosting}>Cancel</Button>
                            <Button onClick={handleCreatePost} disabled={isPosting || !newPost.title.trim() || !newPost.body.trim()}>
                                {isPosting ? (
                                    <span className="inline-flex items-center gap-2">
                                        <IconLoader2 className="size-4 animate-spin" /> Posting…
                                    </span>
                                ) : (
                                    "Post"
                                )}
                            </Button>
                        </CardFooter>

                        {isPosting && (
                            <div className="absolute inset-0 grid place-items-center rounded-xl bg-black/10 backdrop-blur-sm">
                                <div className="flex flex-col items-center gap-2 p-4">
                                    <IconLoader2 className="size-6 animate-spin text-primary" />
                                    <p className="text-sm text-muted-foreground">Posting your update…</p>
                                </div>
                            </div>
                        )}
                    </Card>
                </div>
            )}
        </div>
    );
}
