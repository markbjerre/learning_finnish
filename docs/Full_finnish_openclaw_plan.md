# Suomen Oppiminen 🇫🇮

## Finnish Learning System — Architecture & Project Plan (v2)

---

## Implementation Status (Feb 19, 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI backend | Done | `backend/app/main.py` |
| Spaced repetition engine | Done | `backend/app/services/spaced_repetition.py` |
| Exercise endpoints | Done | `GET /api/exercise/next`, `POST /api/exercise/result`, `GET /api/exercise/history` |
| Word add + inflections | Done | `POST /api/words/add`, `GET /api/words/{id}/inflections` |
| LLM inflection generation | Done | `backend/app/services/inflection_service.py` (OpenAI) |
| Settings & stats | Done | `GET/PUT /api/settings`, `GET /api/stats` |
| Concepts CRUD | Done | `GET/POST/PUT/DELETE /api/concepts` |
| Auth middleware | Done | Optional Bearer token when `FINNISH_API_KEY` set |
| Migration script | Done | `backend/scripts/migrate_spaced_repetition.py` |
| Test script | Done | `scripts/test_db_and_api.py --in-process` |
| OpenClaw skill | Done | `openclaw-skill/finnish-trainer/` (SKILL.md, generate.md, score.md) |
| React dashboard | Done | `/dashboard` — stats, level, exercise history, streak, progress chart |
| Word entry form | Done | Add Word tab with inflection display |
| Concepts UI | Done | `/concepts` — CRUD for grammatical concepts |
| Word list view | Done | Vocabulary tab — searchable, filterable table |
| Bulk CSV import | Done | Bulk Import tab — paste CSV, batch add words |
| OpenClaw cron | Pending | User configures `openclaw cron add` |

---

## 1. System Overview

A spaced-repetition Finnish learning system spanning three components, all coordinated through a Python API on your VPS.

```
┌─────────────────────────────────────────────┐
│           YOUR HOBBY WEBSITE                │
│      (React + Vite + TS + Tailwind)         │
│                                             │
│  ┌───────────┐ ┌────────┐ ┌─────────────┐  │
│  │ Word      │ │Concept │ │ Progress    │  │
│  │ Entry +   │ │ Entry  │ │ Dashboard   │  │
│  │ Inflect.  │ │        │ │             │  │
│  └─────┬─────┘ └───┬────┘ └──────▲──────┘  │
│        │            │             │          │
└────────┼────────────┼─────────────┼──────────┘
         │            │             │
         ▼            ▼             │
┌─────────────────────────────────────────────┐
│         PYTHON FASTAPI (on VPS)             │
│                                             │
│  /words  /concepts  /exercise  /stats       │
│  /words/:id/inflections (LLM-generate)      │
│                                             │
│  Smart word selection:                      │
│    70-80% weakest words (highest priority)  │
│    20-30% random for variety                │
└────────┬────────────────────────┬────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐  ┌───────────────────────┐
│   POSTGRESQL     │  │   OPENCLAW AGENT      │
│   (on VPS)       │  │   (on VPS)            │
│                  │  │                       │
│  words           │  │  Cron (daily 07:00)   │
│  inflections     │  │  → fetch words        │
│  concepts        │  │  → generate exercise  │
│  exercise_log    │  │  → WhatsApp send      │
│                  │  │  → score reply        │
│                  │  │  → update DB          │
│                  │  │                       │
│                  │  │  Ad-hoc:              │
│                  │  │  "add word X" via     │
│                  │  │  WhatsApp → API       │
└──────────────────┘  └───────────────────────┘
```

### Data Flow

1. **You** add Finnish words via the website OR tell OpenClaw on WhatsApp
2. **API receives** the word → calls LLM to generate all inflections → stores everything
3. **OpenClaw cron** fires each morning
4. **API** `/exercise/next` selects words: 70-80% highest priority + 20-30% random
5. **LLM generates** 2-3 Finnish sentences at your current level (e.g. 15/100)
6. **OpenClaw sends** the exercise to WhatsApp
7. **You reply** with your Finnish attempt
8. **LLM evaluates** (kasus, spelling, grammar) → score 0-10 per word
9. **API** updates priorities: well-scored words decay, poorly-scored words stay high
10. **Priority recalculation** accounts for total word count to prevent backlog
11. **Dashboard** shows progress, weak spots, inflection tables

---

## 2. Database Schema

### Design Principles

- **Event-driven priority only** — no time-based decay. If you pause for 2 weeks, scores are unchanged when you return.
- Priority decreases are proportional to vocabulary size, so adding 50 new words doesn't flood you.
- Words scored well in exercises lose priority; words scored poorly retain high priority.
- Each exercise batch: ~70-80% weakest words + ~20-30% randomized for variety.

### Tables

```sql
-- Core vocabulary
CREATE TABLE words (
    id                SERIAL PRIMARY KEY,
    finnish           TEXT NOT NULL,          -- base/dictionary form
    danish            TEXT,                   -- preferred translation
    english           TEXT,                   -- fallback translation
    word_type         TEXT NOT NULL,          -- 'noun', 'verb', 'adjective', 'adverb', 'phrase', 'other'
    grammatical_notes TEXT,                   -- free-text hints
    tags              TEXT[],                 -- e.g. {'food', 'travel', 'daily'}

    -- Spaced repetition state
    priority          FLOAT DEFAULT 1.0,     -- 1.0 = needs practice, 0.0 = mastered
    times_served      INT DEFAULT 0,
    total_score       FLOAT DEFAULT 0.0,     -- sum of all scores (for computing avg)
    last_score        FLOAT,                 -- most recent score
    last_served       TIMESTAMPTZ,

    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Finnish inflections for each word
-- Populated by LLM when a word is added
CREATE TABLE inflections (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    case_name     TEXT NOT NULL,             -- e.g. 'nominatiivi', 'partitiivi', 'genetiivi'
    singular      TEXT,
    plural        TEXT,
    notes         TEXT,                      -- irregularity notes
    UNIQUE(word_id, case_name)
);

-- Verb conjugations (separate because verbs inflect differently)
CREATE TABLE verb_forms (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    form_name     TEXT NOT NULL,             -- e.g. 'minä/preesens', 'sinä/preesens', 'passiivi'
    form_value    TEXT NOT NULL,
    tense         TEXT,                      -- 'preesens', 'imperfekti', 'konditionaali', etc.
    notes         TEXT,
    UNIQUE(word_id, form_name, tense)
);

-- Broader grammatical concepts
CREATE TABLE concepts (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,             -- e.g. 'Partitiivi', 'Verbityypit 1'
    description   TEXT,
    examples      JSONB,                    -- structured examples
    tags          TEXT[],

    -- Spaced repetition state (same model as words)
    priority      FLOAT DEFAULT 1.0,
    times_served  INT DEFAULT 0,
    total_score   FLOAT DEFAULT 0.0,
    last_score    FLOAT,
    last_served   TIMESTAMPTZ,

    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Link words to concepts
CREATE TABLE word_concepts (
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    concept_id    INT REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (word_id, concept_id)
);

-- Exercise history
CREATE TABLE exercise_log (
    id              SERIAL PRIMARY KEY,
    exercise_type   TEXT NOT NULL,           -- 'translation', 'fill_blank', 'conjugation'
    level_used      INT,                     -- e.g. 15 (out of 100)
    words_used      INT[],                   -- word IDs
    concepts_used   INT[],                   -- concept IDs
    prompt_sent     TEXT,                    -- what OpenClaw sent
    user_response   TEXT,                    -- what you replied
    ai_feedback     TEXT,                    -- LLM correction/explanation
    word_scores     JSONB,                   -- [{word_id, score, feedback}]
    concept_scores  JSONB,                   -- [{concept_id, score, feedback}]
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- System settings (level, preferences)
CREATE TABLE settings (
    key           TEXT PRIMARY KEY,
    value         JSONB NOT NULL
);

-- Initialize level
INSERT INTO settings (key, value) VALUES ('level', '15');
INSERT INTO settings (key, value) VALUES ('exercise_word_count', '5');
INSERT INTO settings (key, value) VALUES ('random_ratio', '0.25');
```

### Priority Update Logic (Event-Driven)

The key insight: when an exercise completes, words that scored well **decay proportionally to the total vocabulary size**. This prevents backlog when you add many words.

```python
def update_priorities_after_exercise(db, word_scores: list[dict]):
    """
    Called after each exercise is scored.
    
    word_scores: [{"word_id": 1, "score": 7.5}, ...]
    """
    total_words = db.execute("SELECT COUNT(*) FROM words").scalar()
    
    # Decay factor scales with vocabulary size
    # With 30 words: decay = 0.033 per point
    # With 200 words: decay = 0.005 per point
    # This means larger vocabularies cycle more slowly = no backlog
    decay_per_point = 1.0 / total_words
    
    for ws in word_scores:
        word_id = ws["word_id"]
        score = ws["score"]  # 0-10
        
        # High score (8-10) → priority drops significantly
        # Low score (0-3) → priority stays high or increases
        # Formula: priority_change = (score - 5) * decay_per_point
        #   score 10 → decrease by 5 * decay_per_point
        #   score 5  → no change
        #   score 0  → increase by 5 * decay_per_point
        priority_change = (score - 5) * decay_per_point
        
        db.execute("""
            UPDATE words SET
                priority = GREATEST(0.0, LEAST(1.0, priority - :change)),
                times_served = times_served + 1,
                total_score = total_score + :score,
                last_score = :score,
                last_served = NOW()
            WHERE id = :word_id
        """, {"change": priority_change, "score": score, "word_id": word_id})
```

### Word Selection Logic

```python
def select_exercise_words(db, count: int = 5, random_ratio: float = 0.25):
    """
    Select words for an exercise:
    - ~75% highest priority (weakest words)
    - ~25% random from the full pool (variety + reinforcement)
    """
    n_random = max(1, round(count * random_ratio))
    n_priority = count - n_random
    
    # Highest priority words (excluding ones served today)
    priority_words = db.execute("""
        SELECT id, finnish, danish, english, word_type, priority
        FROM words
        WHERE last_served IS NULL
           OR last_served < CURRENT_DATE
        ORDER BY priority DESC
        LIMIT :n
    """, {"n": n_priority}).fetchall()
    
    # Random words (excluding already selected)
    priority_ids = [w.id for w in priority_words]
    random_words = db.execute("""
        SELECT id, finnish, danish, english, word_type, priority
        FROM words
        WHERE id != ALL(:exclude)
        ORDER BY RANDOM()
        LIMIT :n
    """, {"exclude": priority_ids, "n": n_random}).fetchall()
    
    return priority_words + random_words
```

---

## 3. API Layer — Python FastAPI

Runs on your VPS alongside OpenClaw and PostgreSQL.

### Project Structure

```
finnish-api/
├── main.py                  # FastAPI app + routes
├── models.py                # Pydantic schemas
├── database.py              # DB connection + helpers
├── priority.py              # Priority update + word selection logic
├── inflection_generator.py  # LLM calls to generate inflections
├── requirements.txt         # fastapi, uvicorn, asyncpg, httpx
└── .env                     # DB credentials, API keys
```

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/words` | List words (filter by type, tag, priority range) |
| `POST` | `/api/words` | Add word → triggers LLM inflection generation |
| `PUT` | `/api/words/:id` | Edit a word |
| `DELETE` | `/api/words/:id` | Remove a word |
| `GET` | `/api/words/:id/inflections` | Get all inflections for a word |
| `POST` | `/api/words/:id/inflections/generate` | Re-generate inflections via LLM |
| `GET` | `/api/concepts` | List concepts |
| `POST` | `/api/concepts` | Add concept → triggers LLM example generation |
| `PUT` | `/api/concepts/:id` | Edit a concept |
| `DELETE` | `/api/concepts/:id` | Remove a concept |
| `GET` | `/api/exercise/next` | Smart word selection (priority + random mix) |
| `POST` | `/api/exercise/result` | Submit scores → update priorities |
| `GET` | `/api/exercise/history` | Past exercises with scores |
| `GET` | `/api/stats` | Dashboard data |
| `GET` | `/api/settings` | Get current settings (level, etc.) |
| `PUT` | `/api/settings` | Update settings |

### LLM Inflection Generation

When a word is added (via website or OpenClaw), the API calls the LLM to generate inflections:

```python
INFLECTION_PROMPT = """
Generate all Finnish grammatical forms for the word: "{word}" ({word_type})
Translation: {danish} / {english}

For nouns, provide singular and plural for these cases:
nominatiivi, genetiivi, partitiivi, inessiivi, elatiivi, illatiivi,
adessiivi, ablatiivi, allatiivi, essiivi, translatiivi, abessiivi

For verbs, provide these forms:
minä, sinä, hän, me, te, he (preesens)
minä, sinä, hän, me, te, he (imperfekti)
passiivi (preesens), passiivi (imperfekti)
konditionaali (minä), imperatiivi (sinä)
1. infinitiivi, 3. infinitiivi (inessiivi)

For adjectives, provide:
nominatiivi, partitiivi, genetiivi (singular + plural)
komparatiivi, superlatiivi

Return ONLY this JSON (no other text):
{
  "inflections": [
    {"case_name": "nominatiivi", "singular": "...", "plural": "..."},
    ...
  ],
  "verb_forms": [
    {"form_name": "minä/preesens", "form_value": "...", "tense": "preesens"},
    ...
  ],
  "notes": "any irregularity or important notes"
}
"""
```

### Security

```python
# Simple API key auth — shared between website and OpenClaw
API_KEY = os.getenv("FINNISH_API_KEY")

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if key != API_KEY:
            return JSONResponse(status_code=401, content={"error": "unauthorized"})
    return await call_next(request)
```

---

## 4. Website Features

### Word Entry Page
- Form: finnish, danish, english, word_type (dropdown), tags
- On submit → API creates word → LLM generates inflections (show loading spinner)
- After inflections return, display the full inflection table for review
- Edit/correct inflections manually if the LLM got something wrong

### Inflection Display
- Expandable card per word showing all cases/forms in a clean table
- Nouns: case × singular/plural grid
- Verbs: person × tense grid
- Color-code by mastery (green = low priority, red = high priority)

### Concept Entry Page
- Name, description, tags
- LLM-generated examples on creation
- Link to relevant words

### Progress Dashboard
- **Level indicator**: current level (e.g. 15/100) with manual adjust
- **Mastery overview**: % of words below priority 0.2
- **Word cloud or list**: colored by priority (red → green)
- **Weak spots**: highest priority words + concepts
- **Exercise history**: scrollable list with scores and AI feedback
- **Streak tracker**: consecutive days with completed exercises
- **Stats**: total words, avg score, words mastered this week

### Bulk Import
- Paste or upload CSV: finnish, danish, english, word_type
- Batch LLM inflection generation (with progress indicator)

---

## 5. OpenClaw Integration

### Token-Efficient Architecture

```
OpenClaw Cron (daily 07:00)
    │
    ├─ 1. HTTP GET /api/exercise/next
    │     → returns ~5 words with translations (tiny JSON, ~200 tokens)
    │     → also returns current level from settings
    │
    ├─ 2. LLM call #1 — generate exercise (~300-400 tokens total)
    │     System: "You are a Finnish tutor. Level: 15/100."
    │     User: "Make 2-3 sentences with these words: [small list]"
    │     → structured JSON output
    │
    ├─ 3. Format + send to WhatsApp
    │
    │   ... you reply ...
    │
    ├─ 4. LLM call #2 — score response (~300-400 tokens total)
    │     "Score this attempt. Return JSON only."
    │     → [{word_id, score, feedback}]
    │
    └─ 5. HTTP POST /api/exercise/result
          → API handles all priority math (zero LLM tokens)

Daily cost: ~600-800 tokens ≈ practically free
```

### Skill Files

**`~/.openclaw/skills/finnish-trainer/SKILL.md`**:
```markdown
---
name: Finnish Trainer
description: Daily Finnish language exercises with AI scoring and spaced repetition
triggers:
  - finnish exercise
  - suomi
  - finnish drill
  - add finnish word
---

# Finnish Trainer

## Overview
Generates Finnish language exercises, scores responses, and manages vocabulary
through a spaced repetition system.

## API Base URL
http://localhost:8000/api

## Auth
All API calls need header: Authorization: Bearer {FINNISH_API_KEY}

## Daily Exercise Flow
1. GET /exercise/next → receive words + level
2. Generate 2-3 sentences using those words at the given level
3. Send to user on WhatsApp
4. When user replies, score their response
5. POST /exercise/result with scores

## Adding Words
When the user says "add word [finnish] = [danish/english]":
1. POST /words with the word details
2. Inflections are auto-generated by the API
3. Confirm to user: "Added [word] with [N] inflections"

## Exercise Generation Rules
- Use the level from the API response (e.g. 15/100) to calibrate difficulty
- Level 1-20: very simple sentences, basic vocabulary, present tense
- Level 21-40: compound sentences, past tense, common cases
- Level 41-60: complex grammar, rarer cases, varied tenses
- Level 61-80: nuanced expression, idioms, conditional
- Level 81-100: near-native complexity

## Scoring Rules
- Score each word 0-10
- Consider: correct case/kasus, spelling, word order, verb form
- Provide feedback in Danish
- Return structured JSON only
```

**`~/.openclaw/skills/finnish-trainer/generate.md`**:
```markdown
You are a Finnish language tutor for a Danish-speaking student.

Current level: {{level}}/100

Words to practice:
{{words_json}}

Concepts to reinforce:
{{concepts_json}}

Generate exactly 2-3 Finnish sentences that:
- Use as many of the given words as possible in natural contexts
- Exercise the listed grammatical concepts (especially kasus/cases)
- Match difficulty to level {{level}}/100
- Feel natural, not contrived

Return ONLY this JSON:
[{
  "finnish": "the Finnish sentence",
  "danish": "Danish translation",
  "words_exercised": [list of word_ids used],
  "concepts_exercised": [list of concept_ids used],
  "hint": "brief grammar hint in Danish if helpful"
}]
```

**`~/.openclaw/skills/finnish-trainer/score.md`**:
```markdown
You are scoring a Finnish language exercise for a Danish-speaking student.

The exercise:
{{exercise_json}}

The student's response:
{{user_response}}

Score each word used on 0-10:
- 10: Perfect usage, spelling, grammar
- 7-9: Minor errors (small typo, slightly awkward but correct)
- 4-6: Partially correct (right word, wrong case/form)
- 1-3: Attempted but mostly wrong
- 0: Missing or completely wrong

Return ONLY this JSON:
{
  "word_scores": [
    {"word_id": N, "score": N, "feedback": "brief correction in Danish"}
  ],
  "concept_scores": [
    {"concept_id": N, "score": N, "feedback": "brief explanation in Danish"}
  ],
  "overall_feedback": "1-2 sentences: encouragement + key correction in Danish"
}
```

### OpenClaw Cron Setup

```bash
openclaw cron add --schedule "0 7 * * *" --message "Run the Finnish trainer daily exercise"
```

### Ad-Hoc Word Addition via WhatsApp

When you message OpenClaw something like:
> "add finnish word: talo = hus / house (noun)"

The skill should parse this and `POST /api/words` — the API handles inflection generation automatically.

---

## 6. Project Phases

### Phase 1: Database & API Foundation
**Goal**: Working API on VPS with smart word selection.

| # | Task | Details |
|---|------|---------|
| 1.1 | PostgreSQL setup | Install/configure on VPS, create database |
| 1.2 | Create schema | All tables from Section 2 |
| 1.3 | FastAPI project | Scaffold `finnish-api/` with project structure |
| 1.4 | Word CRUD | `GET/POST/PUT/DELETE /api/words` |
| 1.5 | Concept CRUD | `GET/POST/PUT/DELETE /api/concepts` |
| 1.6 | LLM inflection generator | `POST /words` triggers inflection generation |
| 1.7 | Exercise word selection | `GET /exercise/next` with priority + random mix |
| 1.8 | Exercise scoring endpoint | `POST /exercise/result` with priority update logic |
| 1.9 | Settings + stats endpoints | Level, dashboard data |
| 1.10 | Auth middleware | Bearer token check |
| 1.11 | Seed initial data | Import your existing word list |
| 1.12 | Deploy + test | Run with uvicorn, test all endpoints with curl |

**Deliverable**: API running on VPS, accessible by website and OpenClaw.

---

### Phase 2: Website — Word Management
**Goal**: Add and browse vocabulary with auto-generated inflections.

| # | Task | Details |
|---|------|---------|
| 2.1 | API client | TypeScript fetch wrapper with auth for all endpoints |
| 2.2 | Word entry form | Finnish, danish, english, type dropdown, tags |
| 2.3 | Inflection display | Auto-generated table shown after word creation |
| 2.4 | Word list view | Searchable, filterable, sortable table |
| 2.5 | Inline word editing | Click to edit any word + manually fix inflections |
| 2.6 | Concept entry + display | Form + linked words |
| 2.7 | Bulk import | CSV paste/upload → batch creation with progress bar |
| 2.8 | Word detail page | Full inflection grid, exercise history for that word |

**Deliverable**: Full vocabulary management through your website.

---

### Phase 3: OpenClaw — Daily Exercises
**Goal**: Receive Finnish exercises on WhatsApp every morning.

| # | Task | Details |
|---|------|---------|
| 3.1 | Skill folder setup | Create `~/.openclaw/skills/finnish-trainer/` |
| 3.2 | SKILL.md | Main skill file with triggers and instructions |
| 3.3 | Generate prompt | `generate.md` with level calibration |
| 3.4 | HTTP tool config | Point OpenClaw at your API |
| 3.5 | Exercise flow | Fetch words → generate → format → send on WhatsApp |
| 3.6 | Cron job | `openclaw cron add` for daily 07:00 |
| 3.7 | Test + iterate | Verify sentences are natural and level-appropriate |

**Deliverable**: Daily Finnish exercise on WhatsApp.

---

### Phase 4: OpenClaw — Scoring & Feedback
**Goal**: Replies get scored, priorities update, you get corrections.

| # | Task | Details |
|---|------|---------|
| 4.1 | Response capture | OpenClaw reads your WhatsApp reply |
| 4.2 | Score prompt | `score.md` producing structured JSON |
| 4.3 | Score submission | POST to `/api/exercise/result` |
| 4.4 | Priority verification | Check that priorities shift correctly |
| 4.5 | Feedback message | Send AI corrections back on WhatsApp |
| 4.6 | Ad-hoc word add | "add word X" flow via WhatsApp → API |
| 4.7 | Edge cases | No reply, "skip", gibberish, multi-message |

**Deliverable**: Complete learning loop with scoring.

---

### Phase 5: Progress Dashboard
**Goal**: Visualize your learning journey.

| # | Task | Details |
|---|------|---------|
| 5.1 | Stats API | Aggregated data endpoint |
| 5.2 | Level display | Current level with adjust control |
| 5.3 | Mastery overview | % words at low priority, word count by status |
| 5.4 | Progress chart | Mastery over time (Recharts line/area chart) |
| 5.5 | Weak words | Table of highest-priority words |
| 5.6 | Exercise history | Scrollable feed with scores + feedback |
| 5.7 | Streak counter | Consecutive exercise days |

**Deliverable**: Motivating dashboard on your website.

---

### Phase 6: Polish & Expand
**Goal**: Refine based on real usage.

| # | Task | Details |
|---|------|---------|
| 6.1 | Prompt tuning | Adjust based on exercise quality |
| 6.2 | Exercise variety | Fill-in-the-blank, conjugation drills |
| 6.3 | Auto level-up | Suggest level increase when avg scores are high |
| 6.4 | Weekly summary | OpenClaw sends progress summary |
| 6.5 | Concept auto-linking | LLM suggests word↔concept links |
| 6.6 | Export/backup | CSV/JSON export of vocabulary + scores |

---

## 7. Key Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority decay | Event-driven only | Pause-safe; no backlog when you take a break |
| Decay scaling | Proportional to vocab size | 200 words decay slower per exercise than 30 words |
| Word selection | 75% priority + 25% random | Focused practice with variety to prevent staleness |
| Inflections | LLM-generated on word creation | No manual typing; stored in DB for fast display |
| Difficulty | Level 1-100 system | Granular control, easy to adjust |
| API language | Python FastAPI | Comfortable for you, fast, async-ready |
| LLM calls/day | ~2 small calls (~700 tokens) | Minimal cost |
| Feedback language | Danish | Native language for clearest understanding |
| Deployment | Single VPS | API + DB + OpenClaw co-located, minimal latency |

---

## 8. Quick Start (Minimum Viable Loop)

Get a working exercise loop in a weekend:

1. **Create tables** — run the SQL schema on your VPS PostgreSQL
2. **Scaffold FastAPI** — `main.py` with 4 endpoints: `POST /words`, `GET /exercise/next`, `POST /exercise/result`, `GET /settings`
3. **Seed 20 words** — manually or small script, skip inflections for now
4. **Create OpenClaw skill** — `SKILL.md` + `generate.md` + `score.md`
5. **Set cron** — `openclaw cron add --schedule "0 7 * * *"`
6. **Do your first exercise** — everything else is polish

Then layer on: inflection generation, website UI, dashboard, bulk import.