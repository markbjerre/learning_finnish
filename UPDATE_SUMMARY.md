# Learning Finnish — Update Summary

**Date:** February 19, 2026  
**Status:** DB setup complete | Spaced repetition engine | Test & seed scripts ready | Homelab PostgreSQL via Tailscale

---

## Overview

Learning Finnish uses PostgreSQL on the homelab (external drive) with VPS access via Tailscale. The app uses the `app` schema to avoid conflict with homelab `public.words` (integer id). Spaced repetition engine added for OpenClaw integration.

```
Your PC (Windows)                VPS (72.61.179.126)
     |                               |
     | SSH                           | Tailscale VPN
     v                               v
Homelab (192.168.0.252)  <--- dobbybrain:5433 ---> FastAPI
     |                               |
     v                               v
finnish-db (PostgreSQL on /mnt/seagate_8TB/)
```

---

## Spaced Repetition (OpenClaw)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/exercise/next` | GET | Get words + concepts for daily exercise |
| `/api/exercise/result` | POST | Submit scores, update priorities |
| `/api/exercise/history` | GET | Past exercise log |
| `/api/words` | GET | List words (search, filter, pagination) |
| `/api/words` or `/api/words/add` | POST | Add word (triggers LLM inflection generation) |
| `/api/words/bulk-add` | POST | Bulk add words (rows or csv) |
| `/api/words/{id}/inflections` | GET | Get inflection table for a word |
| `/api/words/{id}/inflections/generate` | POST | Regenerate inflections via LLM |
| `/api/concepts` | GET | List concepts |
| `/api/concepts` | POST | Create concept |
| `/api/settings` | GET/PUT | Level, exercise_word_count, random_ratio |
| `/api/stats` | GET | Dashboard: mastered, learning, needs_work |

**Engine:** Event-driven priority (75% highest-priority + 25% random), decay scales with vocabulary size.

---

## Traefik Routing (VPS)

**405 fix (Feb 2026):** The frontend (`ai-vaerksted-app`) must NOT include `PathPrefix(/finnish)` in its Traefik rule. Finnish traffic goes to `ai-vaerksted-finnish` only. If the frontend catches `/finnish`, POST requests return 405 (Flask has GET-only routes).

- **External:** `https://ai-vaerksted.cloud/finnish/api/...` → Finnish container (prefix stripped)
- **Internal:** `http://ai-vaerksted-finnish:8000/api/...` (OpenClaw on same Docker network)

---

## Database Schema

- **Schema:** `app` (PostgreSQL) — avoids conflict with homelab `public.words`
- **SQLite:** No schema; tables in default namespace
- **Tables:** `lessons`, `users`, `words`, `vocabulary_lists`, `vocabulary_words`, `exercises`, `user_words`, `lesson_progress`, `exercise_results`, `inflections`, `verb_forms`, `concepts`, `word_concepts`, `spaced_exercise_log`, `app_settings`

---

## Migration (Spaced Repetition)

**File:** `backend/scripts/migrate_spaced_repetition.py`

Adds spaced repetition columns to `words` and creates `app_settings` with defaults.

```bash
cd backend
python scripts/migrate_spaced_repetition.py           # PostgreSQL
python scripts/migrate_spaced_repetition.py --use-sqlite  # SQLite
```

---

## Test Script

**File:** `scripts/test_db_and_api.py`

Tests DB connection and API endpoints (including spaced repetition).

```bash
# DB only (PostgreSQL from .env)
python scripts/test_db_and_api.py --db-only

# DB only (SQLite for local testing)
python scripts/test_db_and_api.py --db-only --use-sqlite

# Full test (DB + API) — in-process, no server needed
python scripts/test_db_and_api.py --use-sqlite --in-process

# API only (default: http://localhost:8001)
python scripts/test_db_and_api.py --api-only

# Production API
python scripts/test_db_and_api.py --base-url https://ai-vaerksted.cloud/finnish
```

---

## Seed Script

**File:** `scripts/seed_data.py`

Inserts 5 example rows into each table via ORM.

```bash
# With PostgreSQL (DATABASE_URL in backend/.env)
python scripts/seed_data.py

# With SQLite (local testing)
python scripts/seed_data.py --use-sqlite
```

**Tables seeded:** lessons, users, words, vocabulary_lists, vocabulary_words, exercises, user_words, lesson_progress, exercise_results

---

## Alternative Seed Options

| File | Purpose |
|------|---------|
| `scripts/seed_data_raw.sql` | Raw SQL inserts with `ON CONFLICT DO NOTHING` |
| `scripts/seed_via_sql.py` | Python script running raw SQL (PostgreSQL, `app` schema) |

---

## Homelab PostgreSQL

| Item | Value |
|------|-------|
| **Host** | 192.168.0.252 (homelab) |
| **Container** | finnish-db |
| **Image** | postgres:15-alpine |
| **Data path** | `/mnt/seagate_8TB/finnish/postgres_data` |
| **Listen** | `0.0.0.0:5433` (Tailscale) |
| **Database** | learning_finnish |
| **User** | learning_finnish |
| **Compose path** | `/home/markbj/homelab/apps/finnish-db/` |

### Connection String (VPS)

```
DATABASE_URL=postgresql+asyncpg://learning_finnish:PASSWORD@dobbybrain:5433/learning_finnish
```

### Local Development

- **PostgreSQL:** Set `DATABASE_URL` in `backend/.env` (e.g. `localhost:5432`)
- **SQLite:** Use `--use-sqlite` or leave `DATABASE_URL` empty — uses `backend/learning_finnish.db`

---

## Deployment

1. Add `FINNISH_DATABASE_URL` to VPS `.env`
2. Build and start `ai-vaerksted-finnish` from main compose
3. Verify: `curl https://ai-vaerksted.cloud/finnish/api/health/simple`

---

## OpenClaw Full Test Prompt

Use the prompt in `openclaw-skill/finnish-trainer/TEST_PROMPT.md` to seed the database (20 words, 3 concepts) and exercise all API endpoints via OpenClaw.

---

## Reference Files

| File | Purpose |
|------|---------|
| `Spaced_repetition_instruction.md` | Spaced repetition implementation spec |
| `Full_finnish_openclaw_plan.md` | OpenClaw architecture & plan |
| `openclaw-skill/finnish-trainer/TEST_PROMPT.md` | Full API test + seed prompt for OpenClaw |
| `finnish_2_0_instructions.md` | DB migration + Tailscale setup |
| `homelab/DEPLOY_VPS_FASTAPI.md` | VPS deployment runbook |
| `homelab/TAILSCALE_SETUP.md` | Tailscale setup |
| `192.168.0.252 control/DobbyBrain_Homelab.instructions.md` | Homelab quick reference |
