"use client";

import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, ShieldCheck, ShieldX, Trash2, UserPlus, Loader2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type GuardianStatus = {
  has_guardian: boolean;
  verified: boolean;
  guardian_email: string | null;
  guardian_name: string | null;
  relationship: string | null;
};

export default function GuardianSettingsPage() {
  const [status, setStatus] = useState<GuardianStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // Form
  const [guardianName, setGuardianName] = useState("");
  const [guardianEmail, setGuardianEmail] = useState("");
  const [relationship, setRelationship] = useState("parent");
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  async function fetchStatus() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/guardian/status`, { headers });
      if (res.ok) {
        setStatus(await res.json());
      }
    } catch {
      // offline
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchStatus();
  }, []);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    if (!guardianEmail.trim()) return;
    setActionLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${API}/api/v1/guardian/register`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          guardian_email: guardianEmail,
          guardian_name: guardianName || "Parent/Guardian",
          relationship,
        }),
      });
      if (res.ok) {
        setMessage({ type: "success", text: "Verification email sent to guardian." });
        setGuardianEmail("");
        setGuardianName("");
        await fetchStatus();
      } else {
        const err = await res.json().catch(() => ({}));
        setMessage({ type: "error", text: err.detail || "Failed to register guardian." });
      }
    } catch {
      setMessage({ type: "error", text: "Network error." });
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRemove() {
    if (!confirm("Remove your guardian? They will no longer receive safety notifications.")) return;
    setActionLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${API}/api/v1/guardian`, {
        method: "DELETE",
        headers,
      });
      if (res.ok) {
        setMessage({ type: "success", text: "Guardian removed." });
        await fetchStatus();
      }
    } catch {
      setMessage({ type: "error", text: "Failed to remove guardian." });
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="w-full max-w-lg space-y-6">
        <div className="text-center space-y-1">
          <Shield className="mx-auto h-10 w-10 text-primary" />
          <h1 className="text-2xl font-bold">Guardian Settings</h1>
          <p className="text-sm text-muted-foreground">
            Manage your safety guardian. They are only contacted when our system detects you may need urgent help.
          </p>
        </div>

        {/* Current status */}
        {status?.has_guardian ? (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Current Guardian</CardTitle>
                {status.verified ? (
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/40 border">
                    <ShieldCheck className="mr-1 h-3 w-3" /> Verified
                  </Badge>
                ) : (
                  <Badge className="bg-yellow-500/20 text-yellow-300 border-yellow-500/40 border">
                    <ShieldX className="mr-1 h-3 w-3" /> Pending
                  </Badge>
                )}
              </div>
              {!status.verified && (
                <CardDescription>
                  A verification email has been sent. Your guardian needs to click the link to verify.
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Name</span>
                  <p className="font-medium">{status.guardian_name || "—"}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Email</span>
                  <p className="font-medium">{status.guardian_email || "—"}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Relationship</span>
                  <p className="font-medium capitalize">{status.relationship || "—"}</p>
                </div>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleRemove}
                disabled={actionLoading}
                className="mt-2"
              >
                <Trash2 className="mr-1 h-4 w-4" /> Remove Guardian
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <UserPlus className="h-5 w-5" /> Add a Guardian
              </CardTitle>
              <CardDescription>
                Your guardian will only be notified when our safety system detects you may need urgent support.
                They will never see your messages or journal entries.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRegister} className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="g-name">Guardian Name</Label>
                  <Input
                    id="g-name"
                    placeholder="Parent or guardian's name"
                    value={guardianName}
                    onChange={(e) => setGuardianName(e.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="g-email">Guardian Email *</Label>
                  <Input
                    id="g-email"
                    type="email"
                    placeholder="parent@example.com"
                    value={guardianEmail}
                    onChange={(e) => setGuardianEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="g-rel">Relationship</Label>
                  <select
                    id="g-rel"
                    value={relationship}
                    onChange={(e) => setRelationship(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                  >
                    <option value="parent">Parent</option>
                    <option value="guardian">Legal Guardian</option>
                    <option value="counselor">School Counselor</option>
                    <option value="other">Other Trusted Adult</option>
                  </select>
                </div>
                <Button type="submit" className="w-full" disabled={actionLoading || !guardianEmail.trim()}>
                  {actionLoading ? (
                    <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Sending...</>
                  ) : (
                    "Send Verification Email"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Message */}
        {message && (
          <div className={`rounded-lg p-3 text-sm ${message.type === "success" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
            {message.text}
          </div>
        )}

        {/* Privacy note */}
        <p className="text-center text-xs text-muted-foreground max-w-sm mx-auto">
          Guardians only receive: severity level, timestamp, and a recommended action.
          Your messages, journal entries, and personal data are never shared.
        </p>

        <div className="text-center">
          <Button variant="ghost" asChild>
            <a href="/dashboard">Back to Dashboard</a>
          </Button>
        </div>
      </div>
    </div>
  );
}
