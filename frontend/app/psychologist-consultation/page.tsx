"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  IconCalendar,
  IconArrowUpRight,
  IconCheck,
  IconLoader2,
  IconStar,
  IconStarFilled,
  IconClock,
  IconWorld,
  IconVideo,
  IconX,
} from "@tabler/icons-react";
import { Separator } from "@/components/ui/separator";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Slot = { day: string; start_time: string; end_time: string; timezone: string };
type Provider = {
  provider_id: string;
  name: string;
  credentials: string;
  specialties: string[];
  languages: string[];
  availability_slots: Slot[];
  session_cost: number;
  teletherapy_platform: string;
  rating: number;
  match_score: number;
  next_available: string;
  bio: string;
  accepts_insurance: boolean;
};
type Booking = {
  booking_id: string;
  provider_name: string;
  day: string;
  start_time: string;
  end_time: string;
  timezone: string;
  platform: string;
  meeting_link: string;
  status: string;
};

function RatingStars({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        n <= Math.round(rating)
          ? <IconStarFilled key={n} className="h-4 w-4 text-yellow-400" />
          : <IconStar key={n} className="h-4 w-4 text-muted-foreground/30" />
      ))}
      <span className="ml-1 text-sm text-muted-foreground">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function PsychologistConsultation() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  // Booking state
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingResult, setBookingResult] = useState<Booking | null>(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [mRes, bRes] = await Promise.all([
          fetch(`${API}/api/v1/teletherapy/matches?limit=6`, { headers }),
          fetch(`${API}/api/v1/teletherapy/bookings`, { headers }),
        ]);
        if (mRes.ok) setProviders((await mRes.json()).providers || []);
        if (bRes.ok) setBookings(((await bRes.json()).bookings || []).filter((b: Booking) => b.status === "confirmed"));
      } catch { /* offline */ }
      setLoading(false);
    }
    load();
  }, []);

  async function handleBook() {
    if (!selectedProvider || !selectedSlot) return;
    setBookingLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/teletherapy/book`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          provider_id: selectedProvider.provider_id,
          day: selectedSlot.day,
          start_time: selectedSlot.start_time,
          end_time: selectedSlot.end_time,
          timezone: selectedSlot.timezone,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setBookingResult(data);
        setBookings((prev) => [data, ...prev]);
      }
    } catch { /* */ }
    setBookingLoading(false);
  }

  async function handleCancel(id: string) {
    if (!confirm("Cancel this session?")) return;
    await fetch(`${API}/api/v1/teletherapy/bookings/${id}`, { method: "DELETE", headers });
    setBookings((prev) => prev.filter((b) => b.booking_id !== id));
  }

  function closeModal() {
    setSelectedProvider(null);
    setSelectedSlot(null);
    setBookingResult(null);
  }

  return (
    <div className="relative w-full min-h-screen pt-20 pb-16">
      <div className="mx-auto max-w-6xl px-4">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-2">
          <Badge variant="outline" className="w-fit border-primary/30 bg-primary/5 text-primary">
            <IconVideo className="mr-1 size-4" /> Professional Consultation
          </Badge>
          <h1 className="text-3xl font-semibold tracking-tight">Book a Counselor</h1>
          <p className="text-muted-foreground max-w-xl">
            Licensed professionals matched to your needs. Select a counselor and pick a time that works for you.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <IconLoader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
            {/* Providers */}
            <div className="space-y-4">
              {providers.length === 0 ? (
                <Card>
                  <CardContent className="py-12 text-center text-muted-foreground">
                    No counselors available at the moment. Please check back later.
                  </CardContent>
                </Card>
              ) : (
                providers.map((p) => (
                  <Card key={p.provider_id}>
                    <CardContent className="p-5">
                      <div className="flex gap-4">
                        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
                          {p.name.split(" ").map((w) => w[0]).join("").slice(0, 2)}
                        </div>
                        <div className="flex-1 space-y-2">
                          <div>
                            <h3 className="text-lg font-semibold">{p.name}</h3>
                            <p className="text-sm text-muted-foreground">{p.credentials}</p>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {p.specialties.map((s) => (
                              <Badge key={s} variant="outline" className="text-xs capitalize">{s.replace(/_/g, " ")}</Badge>
                            ))}
                          </div>
                          {p.bio && <p className="text-sm text-muted-foreground">{p.bio}</p>}
                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <RatingStars rating={p.rating} />
                            <span className="flex items-center gap-1"><IconClock className="h-3.5 w-3.5" /> {p.next_available}</span>
                            <span className="flex items-center gap-1"><IconWorld className="h-3.5 w-3.5" /> {p.languages.join(", ")}</span>
                            <span className="font-semibold text-foreground">${p.session_cost}/session</span>
                          </div>
                          <Button
                            size="sm"
                            className="mt-2"
                            onClick={() => { setSelectedProvider(p); setSelectedSlot(null); setBookingResult(null); }}
                          >
                            Book Session <IconArrowUpRight className="ml-1 size-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>

            {/* Sidebar: Upcoming sessions + benefits */}
            <div className="space-y-4">
              {bookings.length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <IconCalendar className="size-5" /> Upcoming Sessions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {bookings.map((b) => (
                      <div key={b.booking_id} className="rounded-lg border p-3 space-y-1">
                        <p className="font-medium text-sm">{b.provider_name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{b.day} {b.start_time}—{b.end_time} ({b.timezone})</p>
                        <div className="flex items-center justify-between">
                          <a href={b.meeting_link} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline">
                            Join ({b.platform})
                          </a>
                          <button onClick={() => handleCancel(b.booking_id)} className="text-xs text-red-400 hover:underline">Cancel</button>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Why see a professional?</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  {[
                    "Get personalised strategies for your specific challenges",
                    "Build coping skills with expert guidance",
                    "Identify patterns you might not notice on your own",
                    "Have a safe, confidential space to talk",
                    "Receive clinical support when self-help isn't enough",
                  ].map((t, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <IconCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                      <span>{t}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>

      {/* Booking modal */}
      {selectedProvider && (
        <div className="fixed inset-0 z-50 grid place-items-center">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={closeModal} />
          <Card className="relative z-10 w-[calc(100vw-2rem)] sm:max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{bookingResult ? "Session Booked!" : `Book with ${selectedProvider.name}`}</CardTitle>
                <button onClick={closeModal}><IconX className="h-5 w-5 text-muted-foreground" /></button>
              </div>
              {!bookingResult && <CardDescription>Select a time slot.</CardDescription>}
            </CardHeader>
            <CardContent>
              {bookingResult ? (
                <div className="space-y-4 text-center">
                  <IconCheck className="mx-auto h-10 w-10 text-emerald-500" />
                  <p className="font-medium capitalize">{bookingResult.day} {bookingResult.start_time} — {bookingResult.end_time}</p>
                  <p className="text-sm text-muted-foreground">{bookingResult.timezone}</p>
                  <a href={bookingResult.meeting_link} target="_blank" className="text-primary hover:underline block">{bookingResult.meeting_link}</a>
                  <Button className="w-full" onClick={closeModal}>Done</Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {selectedProvider.availability_slots.map((slot, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedSlot(slot)}
                      className={`w-full rounded-lg border p-3 text-left text-sm transition ${selectedSlot === slot ? "border-primary bg-primary/10" : "border-border hover:border-muted-foreground/40"}`}
                    >
                      <span className="font-medium capitalize">{slot.day}</span> {slot.start_time} — {slot.end_time}
                      <span className="block text-xs text-muted-foreground">{slot.timezone}</span>
                    </button>
                  ))}
                  <Button className="w-full" onClick={handleBook} disabled={!selectedSlot || bookingLoading}>
                    {bookingLoading ? <><IconLoader2 className="mr-1 h-4 w-4 animate-spin" /> Booking...</> : "Confirm Booking"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
