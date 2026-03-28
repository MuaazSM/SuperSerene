# SuperSerene

**AI-Powered Mental Health Triage for Youth**

SuperSerene is a clinical decision system that screens youth (13–24) using validated instruments, scores severity to DSM-5 cutoffs, and routes them to the right level of care — from self-help exercises to crisis intervention.

> Not a chatbot. A triage engine.

---

## The Problem

- **1 in 5** youth face mental health issues (WHO 2024)
- **11-year** average delay before first treatment
- **70%** of affected youth receive no treatment (Lancet 2023)
- **Zero** structured triage systems exist outside clinical settings

## How It Works

```
Screen → Score → Route → Monitor → Escalate
```

1. **Screen** — User takes PHQ-A / GAD-7 / CRAFFT validated assessments
2. **Score** — AI computes clinical severity band (Green → Yellow → Orange → Red)
3. **Route** — Navigation engine maps to personalized care pathway
4. **Monitor** — Dual-layer safety net watches every interaction
5. **Escalate** — Crisis detection triggers helplines + guardian alerts

---

## Features

### Clinical Screening
- PHQ-A (depression, 9 items), GAD-7 (anxiety, 7 items), CRAFFT (substance use, 6 items)
- Scored to DSM-5 severity cutoffs — not mood sliders

### AI Wellness Coach
- LangChain multi-agent orchestrator with 6 specialized agents
- RAG pipeline grounded in 7 clinical psychology texts
- Facet-aware coaching (self-awareness, empathy, self-regulation, motivation, social skills)

### Safety-First Architecture
- **Layer 1:** 30+ pre-compiled regex patterns across 5 risk categories (<1ms)
- **Layer 2:** LLM semantic analysis with structured classification
- Recovery narrative detection to reduce false positives
- Instant escalation to 988 / AASRA / Samaritans in 4 languages

### Guardian System
- Automated alerts for users under 16 at Orange/Red severity
- Email verification flow for guardians
- Privacy-safe: notifications NEVER include user messages
- Immutable audit trail for every notification

### Teletherapy Matching
- Weighted provider scoring: specialty match (0.4) + availability (0.3) + language (0.2) + rating (0.1)
- Session booking with meeting link generation
- 10 sample providers across 3 languages and 4 timezones

### Mood Analytics Dashboard
- Daily mood index with weighted scoring algorithm
- 7-day and 14-day EMA overlays
- Z-score trend detection (DECLINING / STABLE / IMPROVING)
- Per-facet breakdown with sparklines and self-percentile
- PDF report export

### Guided Meditation
- 9 sessions across 3 duration tiers (5 / 10 / 15 min)
- Mood-matched recommendations
- Full-screen player with breathing animation and progress ring
- Pre/post mood tracking with delta display

### Crisis Resources
- 19 verified hotlines across 4 languages (English, Hindi, Spanish, French)
- Language auto-detection (profile → langdetect → keyword heuristics)
- Always accessible from footer — not just during crisis

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI (Python) |
| AI Orchestration | LangChain (6-agent system) |
| LLMs | Gemini 2.0 Flash, Llama 3.1 8B (Groq), GPT-4o Mini (fallback) |
| Embeddings | Google Generative AI → FAISS vector store |
| Screening | PHQ-A, GAD-7, CRAFFT (DSM-5 aligned) |
| Database | MongoDB (10 collections) |
| Voice | ElevenLabs TTS + WebSocket real-time agent |
| Safety | Rule-based keywords + LLM semantic analysis (dual-layer) |
| Notifications | SMTP email (guardian alerts) |
| Deployment | Docker (containerized FE + BE) |

---

## Project Structure

```
├── backend/
│   ├── api/v1/            # REST API routes (auth, chat, journal, analytics, safety, voice)
│   ├── core/              # Orchestrator, safety checker, coach, analytics engine
│   ├── screening/         # PHQ-A, GAD-7, CRAFFT instruments + scoring
│   ├── services/          # Guardian, matching, meditation, crisis resources, audit log
│   ├── routers/           # Teletherapy, guardian, audit, meditation, analytics dashboard, crisis
│   ├── db/                # MongoDB wrapper, repositories, models
│   ├── rag/               # FAISS vector store, conversational RAG pipeline
│   ├── prompts/           # LLM prompt registry
│   ├── tests/             # 174 unit tests across 10 test files
│   └── config/            # YAML config, environment settings
├── frontend/
│   ├── app/               # 25 Next.js pages
│   │   ├── screening/     # Clinical screening flow
│   │   ├── dashboard/     # Emotional fitness cockpit
│   │   ├── moodindex/     # Wellness coach + analytics dashboard
│   │   ├── guidedmeditation/ # Meditation library + player
│   │   ├── teletherapy/   # Provider matching + booking
│   │   ├── crisis-resources/ # Multi-language hotline directory
│   │   ├── journal/       # AI-powered journaling
│   │   ├── exercise/      # 12 guided exercises
│   │   └── settings/      # Guardian management
│   ├── components/        # Reusable UI components
│   └── lib/               # API client, utilities
```

---

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

```env
# Required (at least one LLM provider)
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key

# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB=serene_ai

# Auth
JWT_SECRET=your_secret_key

# Optional
ELEVENLABS_API_KEY=your_key
TAVILY_API_KEY=your_key
SMTP_USER=your_email
SMTP_PASSWORD=your_app_password
```

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
# 174 passed in 0.19s
```

---

## API Endpoints

| Category | Endpoints |
|----------|-----------|
| Auth | `POST /api/v1/auth/signup`, `/login`, `/google/login` |
| Screening | `GET /api/v1/screening/instruments`, `POST /{instrument}/score`, `POST /composite` |
| Chat | `POST /api/v1/chat/sessions/{id}/messages` |
| Analytics | `GET /api/v1/analytics/dashboard/timeline`, `/ema`, `/facets`, `/streaks`, `/trends`, `/export` |
| Journal | `POST /api/v1/journal/analyze-entry` |
| Safety | `POST /api/v1/safety/check` |
| Meditation | `GET /api/v1/meditation/library`, `/recommended`, `POST /{id}/complete` |
| Teletherapy | `GET /api/v1/teletherapy/matches`, `POST /book` |
| Guardian | `POST /api/v1/guardian/register`, `GET /verify/{token}`, `GET /status` |
| Crisis | `GET /api/v1/crisis/resources`, `/nearest?lang=hi` |

---

## Test Coverage

| Module | Tests | Coverage |
|--------|-------|---------|
| Screening instruments (PHQ-A, GAD-7, CRAFFT) | 30 | All severity bands, boundary cases, validation |
| Safety checker | 32 | Keywords, recovery narratives, risk scoring, classification |
| Crisis resources | 22 | 4 languages, filtering, language detection |
| Analytics engine | 21 | Mood scoring, EMA, z-score, trend flags |
| Meditation service | 16 | Library, recommendations, completion tracking |
| Guardian service | 14 | Notification logic, privacy verification, consent |
| Matching service | 11 | Provider scoring, availability, language match |
| Analytics dashboard | 9 | EMA series, period computation |
| Audit log | 3 | Record creation, field validation |
| **Total** | **174** | **100% pass rate** |

---

## Team

**Team Pied Piper**

- Muaaz
- Jugaad
- Mantek
- Vaishnavi

---

## License

This project was built for the Tabhi hackathon.
