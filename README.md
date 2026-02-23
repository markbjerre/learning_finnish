# Learning Finnish

AI-powered Finnish language learning application with spaced repetition for OpenClaw integration.

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI
- **Database:** PostgreSQL (homelab, via Tailscale) or SQLite (local)

## Features

- **Spaced repetition engine** — Event-driven priority (75% weakest + 25% random), OpenClaw-ready
- **LLM inflection generation** — Noun/adjective cases and verb conjugations via OpenAI
- **Exercise flow** — `/api/exercise/next`, `/api/exercise/result`, `/api/stats`

## Database

PostgreSQL runs on the homelab (192.168.0.252) at `/mnt/seagate_8TB/finnish/postgres_data`. The VPS connects via Tailscale at `dobbybrain:5433`.

**Connection string (VPS):**
```
DATABASE_URL=postgresql+asyncpg://learning_finnish:PASSWORD@dobbybrain:5433/learning_finnish
```

**Local:** Set `DATABASE_URL=""` or use `--use-sqlite` for SQLite (`backend/learning_finnish.db`).

## Quick Start

```bash
# Migration (add spaced repetition columns)
cd backend && python scripts/migrate_spaced_repetition.py --use-sqlite

# Run tests (no server needed)
python scripts/test_db_and_api.py --use-sqlite --in-process

# Start API
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Documentation

- **UPDATE_SUMMARY.md** — API reference, deployment, scripts
- **Spaced_repetition_instruction.md** — Implementation spec for spaced repetition
- **Full_finnish_openclaw_plan.md** — OpenClaw architecture & plan
- **finnish_2_0_instructions.md** — DB migration + Tailscale setup
- **homelab/** — Homelab deployment files
- **CLAUDE_DEV.md** — Development guide

## Live

https://ai-vaerksted.cloud/finnish
