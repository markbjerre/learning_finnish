# Learning Finnish — Project Index

**Last updated:** February 2026

## Architecture

React + FastAPI Finnish vocabulary trainer with spaced repetition, MiniMax AI inflection generation, and an OpenClaw skill for daily chat-based exercises.

```
src/                    React frontend (Vite, TypeScript, Tailwind)
backend/app/            FastAPI backend (Python 3.11+)
  main.py               App entry point — mounts all routers
  config.py             Settings: DB, MINIMAX_API_KEY, ports
  routers/              exercise.py, words.py, health.py, …
  services/
    spaced_repetition.py  Word selection (75% priority + 25% random)
    ai_service.py         MiniMax/OpenAI client, definitions, examples
    inflection_service.py Finnish case/verb generation → stored in DB
  models_db.py          SQLAlchemy models (app schema)
openclaw-skill/         OpenClaw Finnish trainer skill
tests/playwright/       Python API tests (smoke, words, exercise)
e2e/                    TypeScript Playwright browser tests
scripts/                test.sh, dev scripts
```

---

## Key Concepts

### Spaced Repetition
- Words have a `priority` score (higher = served more often)
- `GET /api/exercise/next` returns 5 words: 75% highest-priority + 25% random, up to 2 concepts
- `POST /api/exercise/result` updates priority based on score (>5 decreases, <5 increases)
- History logged to `app.spaced_exercise_log`

### AI Inflections (MiniMax)
- Triggered on every `POST /api/words/add`
- Nouns/adjectives → 12 Finnish cases → stored in `app.inflections`
- Verbs → 16 conjugation forms → stored in `app.verb_forms`
- MiniMax returns `<think>…</think>` blocks — stripped by `_extract_json()` before JSON parse
- Key: `MINIMAX_API_KEY` in `backend/.env`

### OpenClaw Integration
- Skill: `openclaw-skill/finnish-trainer/SKILL.md`
- API base (internal): `http://ai-vaerksted-finnish:8000`
- Key endpoints: `GET /api/exercise/next`, `POST /api/exercise/result`, `POST /api/words/add`

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
| `words` | Vocabulary with priority, scores, translations |
| `inflections` | Finnish noun/adj case forms (12 per word) |
| `verb_forms` | Finnish verb conjugations (16 per verb) |
| `concepts` | Grammar concepts shown during exercises |
| `spaced_exercise_log` | Exercise history with scores |
| `app_settings` | Key-value config store |

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/words` | List vocabulary |
| POST | `/api/words/add` | Add word + generate inflections |
| POST | `/api/words/search` | Search by Finnish word |
| GET | `/api/words/{id}/inflections` | Get stored inflections |
| POST | `/api/words/{id}/inflections/generate` | Regenerate inflections |
| GET | `/api/exercise/next` | Get next exercise words |
| POST | `/api/exercise/result` | Submit exercise score |
| GET | `/api/exercise/history` | Exercise history |

Full words API: `backend/WORDS_API_DOCUMENTATION.md`

---

## Documentation Map

| Doc | Purpose |
|-----|---------|
| `CLAUDE.md` | Project config, entry points, AI setup |
| `AGENTS.md` | Agent session guide, test strategy, AI services |
| `docs/INDEX.md` | Full documentation listing |
| `backend/WORDS_API_DOCUMENTATION.md` | Words API reference |
| `openclaw-skill/finnish-trainer/SKILL.md` | OpenClaw skill |
| `homelab/DEPLOY_VPS_FASTAPI.md` | VPS deployment |
| `docs/Spaced_repetition_instruction.md` | Spaced repetition design |
