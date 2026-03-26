"use client";

import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Star,
  Clock,
  Video,
  Globe,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Loader2,
  Calendar,
  X,
} from "lucide-react";

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

function Stars({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          className={`h-3.5 w-3.5 ${n <= Math.round(rating) ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground/30"}`}
        />
      ))}
      <span className="ml-1 text-xs text-muted-foreground">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function TeletherapyPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Booking modal
  const [bookingProvider, setBookingProvider] = useState<Provider | null>(null);
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
        if (mRes.ok) {
          const d = await mRes.json();
          setProviders(d.providers || []);
        }
        if (bRes.ok) {
          const d = await bRes.json();
          setBookings((d.bookings || []).filter((b: Booking) => b.status === "confirmed"));
        }
      } catch { /* offline */ }
      setLoading(false);
    }
    load();
  }, []);

  async function handleBook() {
    if (!bookingProvider || !selectedSlot) return;
    setBookingLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/teletherapy/book`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          provider_id: bookingProvider.provider_id,
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

  async function handleCancel(bookingId: string) {
    if (!confirm("Cancel this session?")) return;
    try {
      const res = await fetch(`${API}/api/v1/teletherapy/bookings/${bookingId}`, {
        method: "DELETE",
        headers,
      });
      if (res.ok) {
        setBookings((prev) => prev.filter((b) => b.booking_id !== bookingId));
      }
    } catch { /* */ }
  }

  function closeModal() {
    setBookingProvider(null);
    setSelectedSlot(null);
    setBookingResult(null);
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-24">
      <div className="mb-8 space-y-2">
        <Badge variant="outline" className="border-primary/30 bg-primary/5 text-primary">
          <Video className="mr-1 h-4 w-4" /> Teletherapy
        </Badge>
        <h1 className="text-3xl font-bold tracking-tight">Find a Counselor</h1>
        <p className="text-muted-foreground max-w-xl">
          Matched to your needs based on your screening results, language, and availability.
        </p>
      </div>

      {/* Provider cards */}
      <div className="space-y-4">
        {providers.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              No providers available right now. Please check back later.
            </CardContent>
          </Card>
        )}

        {providers.map((p) => {
          const expanded = expandedId === p.provider_id;
          return (
            <Card key={p.provider_id} className="overflow-hidden">
              <CardContent className="p-5">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start gap-3">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
                        {p.name.split(" ").map((w) => w[0]).join("").slice(0, 2)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{p.name}</h3>
                        <p className="text-sm text-muted-foreground">{p.credentials}</p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {p.specialties.map((s) => (
                        <Badge key={s} variant="outline" className="text-xs capitalize">
                          {s.replace(/_/g, " ")}
                        </Badge>
                      ))}
                    </div>
                    {p.bio && <p className="text-sm text-muted-foreground">{p.bio}</p>}
                  </div>

                  <div className="flex flex-col items-end gap-2 text-sm text-right shrink-0">
                    <Stars rating={p.rating} />
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Clock className="h-3.5 w-3.5" /> {p.next_available}
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Globe className="h-3.5 w-3.5" /> {p.languages.join(", ")}
                    </div>
                    <div className="font-semibold">
                      ${p.session_cost}
                      <span className="text-xs font-normal text-muted-foreground"> / session</span>
                      {p.accepts_insurance && (
                        <Badge variant="outline" className="ml-2 text-[10px]">Insurance</Badge>
                      )}
                    </div>
                  </div>
                </div>

                {/* Expand/collapse availability */}
                <div className="mt-4 flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setExpandedId(expanded ? null : p.provider_id)}
                  >
                    {expanded ? <ChevronUp className="mr-1 h-4 w-4" /> : <ChevronDown className="mr-1 h-4 w-4" />}
                    {expanded ? "Hide times" : "View all available times"}
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => {
                      setBookingProvider(p);
                      setSelectedSlot(null);
                      setBookingResult(null);
                    }}
                  >
                    Book Session
                  </Button>
                </div>

                {expanded && (
                  <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {p.availability_slots.map((slot, i) => (
                      <div
                        key={i}
                        className="rounded-lg border border-border/70 bg-muted/30 px-3 py-2 text-sm"
                      >
                        <span className="font-medium capitalize">{slot.day}</span>{" "}
                        <span className="text-muted-foreground">
                          {slot.start_time} — {slot.end_time}
                        </span>
                        <span className="block text-xs text-muted-foreground">{slot.timezone}</span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Upcoming sessions */}
      {bookings.length > 0 && (
        <div className="mt-12 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Calendar className="h-5 w-5" /> Your Upcoming Sessions
          </h2>
          {bookings.map((b) => (
            <Card key={b.booking_id}>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <p className="font-medium">{b.provider_name}</p>
                  <p className="text-sm text-muted-foreground capitalize">
                    {b.day} {b.start_time} — {b.end_time} ({b.timezone})
                  </p>
                  <a
                    href={b.meeting_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    Join on {b.platform}
                  </a>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleCancel(b.booking_id)}>
                  Cancel
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Booking modal */}
      {bookingProvider && (
        <div className="fixed inset-0 z-50 grid place-items-center">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={closeModal} />
          <Card className="relative z-10 w-full max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {bookingResult ? "Session Booked!" : `Book with ${bookingProvider.name}`}
                </CardTitle>
                <Button variant="ghost" size="icon" onClick={closeModal}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              {!bookingResult && (
                <CardDescription>Select a time slot for your session.</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {bookingResult ? (
                <div className="space-y-4 text-center">
                  <CheckCircle2 className="mx-auto h-10 w-10 text-emerald-500" />
                  <div className="space-y-1">
                    <p className="font-medium capitalize">
                      {bookingResult.day} {bookingResult.start_time} — {bookingResult.end_time}
                    </p>
                    <p className="text-sm text-muted-foreground">{bookingResult.timezone}</p>
                  </div>
                  <a
                    href={bookingResult.meeting_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block text-primary hover:underline"
                  >
                    {bookingResult.meeting_link}
                  </a>
                  <Button className="w-full" onClick={closeModal}>
                    Done
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {bookingProvider.availability_slots.map((slot, i) => (
                    <button
                      key={i}
                      onClick={() => setSelectedSlot(slot)}
                      className={`w-full rounded-lg border p-3 text-left text-sm transition ${
                        selectedSlot === slot
                          ? "border-primary bg-primary/10"
                          : "border-border hover:border-muted-foreground/40"
                      }`}
                    >
                      <span className="font-medium capitalize">{slot.day}</span>{" "}
                      {slot.start_time} — {slot.end_time}
                      <span className="block text-xs text-muted-foreground">{slot.timezone}</span>
                    </button>
                  ))}
                  <Button
                    className="w-full"
                    onClick={handleBook}
                    disabled={!selectedSlot || bookingLoading}
                  >
                    {bookingLoading ? (
                      <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Booking...</>
                    ) : (
                      "Confirm Booking"
                    )}
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
