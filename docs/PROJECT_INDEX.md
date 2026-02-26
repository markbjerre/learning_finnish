# Learning Finnish — Project Index

**Last updated:** February 2026

## Architecture

React + FastAPI Finnish vocabulary trainer with spaced repetition, MiniMax AI inflection generation, and an OpenClaw skill for daily chat-based exercises.

```
src/                    React frontend (Vite, TypeScript, Tailwind)
backend/app/            FastAPI backend (Python 3.11+)
  main.py               App entry point — mounts all routers
  config.py             Settings: DB, MINIMAX_API_KEY, ports
  routers/              exercise.py, words.py, concepts.py, health.py, …
  services/
    spaced_repetition.py  Word/concept selection + priority updates + mastery
    ai_service.py         MiniMax/OpenAI client, definitions, examples
    inflection_service.py Finnish case/verb generation → stored in DB
  models_db.py          SQLAlchemy models (app schema)
openclaw-skill/         OpenClaw Finnish trainer skill
tests/playwright/       Python API tests (smoke, words, exercise)
e2e/                    TypeScript Playwright browser tests
scripts/                test.sh, dev scripts, migrate_*.py, seed_*.py
```

---

## Key Concepts

### Spaced Repetition
- Words have a `priority` score (higher = served more often)
- `GET /api/exercise/next` returns words (75% highest-priority + 25% random) with inflections eager-loaded
- `POST /api/exercise/result` updates word/concept priority based on score (score >5 decreases priority, <5 increases)
- History logged to `app.spaced_exercise_log`

### Active Concepts
- 30 Finnish grammatical concepts pre-populated with `frequency` (1-5) and `difficulty` (1-5)
- OpenClaw and the website decide which concepts are "active" — the API does not track this
- Mastery (0–10 XP) tracked per user per concept in `app.user_concept_progress`
- Mastery grows `+0.01 × score` per exercise — ~100-1000 exercises to reach 10.0
- `GET /api/concepts?user_id=X` returns mastery for each concept for that user

### Word Normalization
- `POST /api/words` accepts any language input (`"word": "hund"` or `"dog"` or `"koira"`)
- API detects language, translates to Finnish, lemmatizes, detects word type via LLM (MiniMax)
- Returns normalization metadata: `{finnish, danish, english, word_type, was_corrected, valid}`
- Invalid/unrecognizable words return `{"status": "invalid"}`

### AI Inflections (MiniMax)
- Triggered automatically on word add
- Nouns/pronouns → 12 Finnish cases × sg/pl → `app.inflections`
- Adjectives → 12 cases × 3 degrees (base/comparative/superlative) → `app.inflections`
- Verbs → conjugations + infinitives + participles → `app.verb_forms`
- Non-inflecting types (adverb, conjunction, particle, etc.) → no LLM call
- Inflections returned in `GET /api/exercise/next` so LLM generator uses real stored forms
- MiniMax returns `<think>…</think>` blocks — stripped by `_extract_json()` before JSON parse
- Key: `MINIMAX_API_KEY` in `backend/.env`

### OpenClaw Integration
- Skill: `openclaw-skill/finnish-trainer/SKILL.md`
- API base (internal): `http://ai-vaerksted-finnish:8000`
- Words fetched daily via `GET /api/exercise/next`
- Concepts fetched separately — OpenClaw rotates weekly, picks 1-3 active concepts
- Exercise result submitted with `user_id` to track per-user mastery

---

## Database (PostgreSQL 15)

| Detail | Value |
|--------|-------|
| Port | 5433 (homelab, Seagate 8TB) |
| DB | `learning_finnish` |
| Schema | `app` (not `public`) |
| Docker | `~/homelab/apps/finnish-db/docker-compose.yml` |

### Tables (`app` schema)

| Table | Purpose |
|-------|---------|
| `words` | Vocabulary with priority, scores, translations (Finnish/Danish/English) |
| `inflections` | Noun/adj case forms (12 cases × degree); `degree` NULL=base, "comparative", "superlative" |
| `verb_forms` | Verb conjugations, infinitives, participles |
| `concepts` | 30 pre-populated grammar concepts with `name_fi`, `frequency`, `difficulty` |
| `word_concepts` | Many-to-many: words ↔ concepts |
| `users` | User profiles (id, email, username) — no auth |
| `user_words` | Per-user word progress: status (RECENT/LEARNING/MASTERED), proficiency (0-100) |
| `user_concept_progress` | Per-user concept mastery (0-10), exercise_count; lazy-created on first exercise |
| `spaced_exercise_log` | Full exercise history with scores |
| `app_settings` | Key-value config: level, exercise_word_count, random_ratio |

### Known users

| id | username | notes |
|----|----------|-------|
| `user-main-admin` | Main_Admin | Primary user (Mark) — 60 words linked |
| `user-demo-1` | Demo_Beginner | Seed/test user |
| `user-demo-2` | Demo_Intermediate | Seed/test user |
| `user-demo-3` | Demo_Advanced | Seed/test user |

---

## API Endpoints

### Words
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/words` | List vocabulary |
| POST | `/api/words` | Add word (any language — auto-normalized) |
| POST | `/api/words/bulk-add` | Bulk add words |
| POST | `/api/words/search` | Search by Finnish word |
| GET | `/api/words/{id}/inflections` | Get stored inflections |
| POST | `/api/words/{id}/inflections/generate` | Regenerate inflections via LLM |

### Concepts
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/concepts` | List all 30 concepts |
| GET | `/api/concepts?user_id=X` | List with per-user mastery |
| GET | `/api/concepts/{id}?user_id=X` | Single concept + mastery |
| POST | `/api/concepts` | Create concept |
| PUT | `/api/concepts/{id}` | Update concept |
| DELETE | `/api/concepts/{id}` | Delete concept |

### Exercise
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/exercise/next` | Get next words (with inflections) + level |
| POST | `/api/exercise/result` | Submit scores; pass `user_id` for mastery tracking |
| GET | `/api/exercise/history` | Exercise history |

### Other
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET/POST | `/api/settings/{key}` | App settings CRUD |

Full words API: `backend/WORDS_API_DOCUMENTATION.md`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/migrate_spaced_repetition.py` | Add spaced rep fields to words/concepts |
| `scripts/migrate_inflection_degree.py` | Add `degree` column to inflections |
| `scripts/migrate_concepts_mastery.py` | Add `name_fi`/`frequency`/`difficulty` to concepts; create `user_concept_progress` |
| `scripts/backfill_inflections.py` | Generate inflections for words missing them |
| `scripts/seed_concepts_and_users.py` | Seed 30 concepts + 3 demo users (use `--force` to re-seed) |

---

## Documentation Map

| Doc | Purpose |
|-----|---------|
| `CLAUDE.md` | Project config, entry points, AI setup |
| `docs/PROJECT_INDEX.md` | This file — current system overview |
| `backend/WORDS_API_DOCUMENTATION.md` | Words API reference |
| `openclaw-skill/finnish-trainer/SKILL.md` | OpenClaw skill — exercise flow, concept rotation |
| `homelab/DEPLOY_VPS_FASTAPI.md` | VPS deployment |
| `docs/Spaced_repetition_instruction.md` | Spaced repetition design |
