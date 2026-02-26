# Learning Finnish — Claude Configuration

## Type
Mixed

## Entry points
| Action | Command |
|--------|---------|
| **Backend entry** | `backend/app/main.py` (FastAPI, port 8001) |
| **Frontend entry** | `src/App.tsx` (React + Vite, port 5173) |
| **Run backend (Linux)** | `./scripts/dev-finnish.sh` |
| **Run backend (Windows/SQLite)** | `.\scripts\run-backend-local.ps1` |
| **Run backend (homelab DB)** | `.\scripts\run-backend-homelab.ps1` |
| **Run tests** | `./scripts/test.sh` (e2e Playwright + Python API tests) |

## Documentation
See [docs/PROJECT_INDEX.md](docs/PROJECT_INDEX.md) for full architecture, tables, and API reference. Do not create new docs without updating PROJECT_INDEX.md.

## Overview
React + FastAPI Finnish learning app with spaced repetition, per-user concept mastery tracking, and an OpenClaw skill for daily exercises. See root CLAUDE.md for workspace conventions.

## Key Files
- **Architecture:** `docs/PROJECT_INDEX.md` — full system overview, table list, API endpoints
- **Backend services:** `backend/app/services/` — spaced repetition, AI (MiniMax), inflections
- **Config/env:** `backend/app/config.py` + `backend/.env` — DB, `MINIMAX_API_KEY`, ports
- **OpenClaw skill:** `openclaw-skill/finnish-trainer/SKILL.md`
- **API docs:** `backend/WORDS_API_DOCUMENTATION.md`

## AI / Inflections
- MiniMax API (`MINIMAX_API_KEY` in `backend/.env`) generates inflections when words are added
- Uses OpenAI-compatible client pointed at `https://api.minimax.io/v1` with model `MiniMax-M2.5`
- MiniMax returns `<think>…</think>` blocks — `_extract_json()` in both service files strips these
- Nouns → 12 Finnish cases stored in `app.inflections` (degree=NULL)
- Adjectives → 12 cases × 3 degrees (base/comparative/superlative) in `app.inflections`
- Verbs → conjugations + infinitives + participles in `app.verb_forms`
- Non-inflecting types (adverb, conjunction, particle, etc.) → skipped, no LLM call
- Falls back to OpenAI if `OPENAI_API_KEY` set, then mock data if neither key present

## Word Normalization
- `POST /api/words {"word": "hund"}` accepts Finnish, Danish, or English input
- LLM detects language, translates to Finnish lemma, detects word type
- Returns `normalization` metadata including `was_corrected`, `valid`
- Invalid words return `{"status": "invalid"}` — not inserted

## Active Concepts & Mastery
- 30 Finnish grammatical concepts pre-seeded with `frequency` (1-5) and `difficulty` (1-5)
- OpenClaw/website manage which concepts are "active" — API does not track this
- `UserConceptProgress` tracks mastery (0.0–10.0) per user per concept
- Mastery increments `+0.01 × score` per exercise — lazy-created on first exercise
- `POST /api/exercise/result` accepts optional `user_id` to update mastery (backward compatible)

## Users
- Main user: `user-main-admin` (markymark@placeholder.com / Main_Admin) — 60 words linked
- Demo users: `user-demo-1/2/3` for multi-user testing
- No authentication — user_id passed explicitly in requests
