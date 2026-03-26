"use client";

import React, { useEffect, useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Phone, MessageSquare, Globe, Clock, Search, Heart,
  ChevronDown, ChevronUp, Loader2, Shield,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Resource = {
  country: string;
  country_code: string;
  language: string;
  hotline_name: string;
  phone_number: string | null;
  text_line: string | null;
  chat_url: string | null;
  hours: string;
  description: string;
};

const LANG_LABELS: Record<string, string> = {
  en: "English",
  hi: "Hindi",
  es: "Spanish",
  fr: "French",
};

const LANG_FLAGS: Record<string, string> = {
  en: "EN",
  hi: "HI",
  es: "ES",
  fr: "FR",
};

export default function CrisisResourcesPage() {
  const [grouped, setGrouped] = useState<Record<string, Resource[]>>({});
  const [loading, setLoading] = useState(true);
  const [selectedLang, setSelectedLang] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedLangs, setExpandedLangs] = useState<Set<string>>(new Set(["en"]));

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await fetch(`${API}/api/v1/crisis/resources/all`);
        if (res.ok) {
          const data = await res.json();
          setGrouped(data.grouped || {});
          // Expand all languages by default
          setExpandedLangs(new Set(Object.keys(data.grouped || {})));
        }
      } catch {
        // Fallback: hardcoded essential resources always available
        setGrouped({
          en: [
            { country: "United States", country_code: "US", language: "en", hotline_name: "988 Suicide & Crisis Lifeline", phone_number: "988", text_line: "Text 988", chat_url: "https://988lifeline.org/chat/", hours: "24/7", description: "Free, confidential support for people in suicidal crisis or emotional distress." },
            { country: "United Kingdom", country_code: "GB", language: "en", hotline_name: "Samaritans", phone_number: "116 123", text_line: null, chat_url: null, hours: "24/7", description: "Emotional support for anyone in distress or at risk of suicide." },
          ],
          hi: [
            { country: "India", country_code: "IN", language: "hi", hotline_name: "AASRA", phone_number: "91-22-27546669", text_line: null, chat_url: null, hours: "24/7", description: "Crisis intervention centre for the depressed and suicidal." },
          ],
        });
        setExpandedLangs(new Set(["en", "hi"]));
      }
      setLoading(false);
    }
    load();
  }, []);

  const filteredGrouped = useMemo(() => {
    let result = { ...grouped };

    if (selectedLang !== "all") {
      result = { [selectedLang]: result[selectedLang] || [] };
    }

    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      const filtered: Record<string, Resource[]> = {};
      for (const [lang, resources] of Object.entries(result)) {
        const matches = resources.filter(
          (r) =>
            r.hotline_name.toLowerCase().includes(q) ||
            r.country.toLowerCase().includes(q) ||
            r.description.toLowerCase().includes(q) ||
            (r.phone_number || "").includes(q)
        );
        if (matches.length > 0) filtered[lang] = matches;
      }
      return filtered;
    }

    return result;
  }, [grouped, selectedLang, searchQuery]);

  function toggleLang(lang: string) {
    setExpandedLangs((prev) => {
      const next = new Set(prev);
      if (next.has(lang)) next.delete(lang);
      else next.add(lang);
      return next;
    });
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 pb-20 pt-24">
      {/* Header */}
      <div className="mb-8 text-center space-y-3">
        <Shield className="mx-auto h-10 w-10 text-red-400" />
        <h1 className="text-3xl font-bold tracking-tight">Crisis Resources</h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          If you or someone you know is in crisis, please reach out. Help is available 24/7 in multiple languages.
        </p>
      </div>

      {/* Emergency banner */}
      <div className="mb-8 rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-center">
        <p className="text-red-300 font-semibold text-lg">
          In immediate danger? Call your local emergency number (911 / 112 / 999)
        </p>
        <p className="text-red-300/70 text-sm mt-1">
          The resources below are for emotional support and crisis counseling.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center mb-8">
        <div className="flex gap-2 flex-wrap">
          <Button
            size="sm"
            variant={selectedLang === "all" ? "default" : "outline"}
            onClick={() => setSelectedLang("all")}
          >
            All Languages
          </Button>
          {Object.entries(LANG_LABELS).map(([code, name]) => (
            <Button
              key={code}
              size="sm"
              variant={selectedLang === code ? "default" : "outline"}
              onClick={() => setSelectedLang(code)}
            >
              {name}
            </Button>
          ))}
        </div>
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search hotlines..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Resource groups */}
      <div className="space-y-6">
        {Object.entries(filteredGrouped).map(([lang, resources]) => {
          const expanded = expandedLangs.has(lang);
          return (
            <div key={lang}>
              <button
                onClick={() => toggleLang(lang)}
                className="flex w-full items-center justify-between rounded-lg bg-muted/30 px-4 py-3 text-left hover:bg-muted/50 transition"
              >
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="text-xs">
                    {LANG_FLAGS[lang] || lang.toUpperCase()}
                  </Badge>
                  <span className="font-semibold">{LANG_LABELS[lang] || lang}</span>
                  <span className="text-sm text-muted-foreground">({resources.length} resources)</span>
                </div>
                {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>

              {expanded && (
                <div className="mt-3 space-y-3">
                  {resources.map((r, i) => (
                    <ResourceCard key={`${r.hotline_name}-${i}`} resource={r} />
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {Object.keys(filteredGrouped).length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No resources found matching your search.
          </div>
        )}
      </div>

      {/* Footer note */}
      <div className="mt-12 text-center">
        <p className="text-xs text-muted-foreground max-w-md mx-auto">
          These resources are verified from official sources. If you notice an incorrect number,
          please contact us at hello@superserene.app so we can update it immediately.
        </p>
      </div>
    </div>
  );
}

function ResourceCard({ resource: r }: { resource: Resource }) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1.5 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold">{r.hotline_name}</h3>
              <Badge variant="outline" className="text-[10px]">{r.country}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{r.description}</p>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" /> {r.hours}
            </div>
          </div>

          <div className="flex flex-col gap-2 sm:items-end shrink-0">
            {r.phone_number && (
              <a
                href={`tel:${r.phone_number.replace(/[^0-9+]/g, "")}`}
                className="inline-flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-2 text-sm font-medium text-red-300 hover:bg-red-500/20 transition"
              >
                <Phone className="h-4 w-4" /> {r.phone_number}
              </a>
            )}
            {r.text_line && (
              <div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                <MessageSquare className="h-3.5 w-3.5" /> {r.text_line}
              </div>
            )}
            {r.chat_url && (
              <a
                href={r.chat_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <Globe className="h-3.5 w-3.5" /> Online chat
              </a>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
