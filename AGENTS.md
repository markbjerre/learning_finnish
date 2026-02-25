# Learning Finnish — Agent Guide

## Session Start

Read in order:
1. `CLAUDE.md` — project context, architecture, known issues
2. `docs/INDEX.md` — documentation map
3. `git status` — check working tree

---

## Entry Points

| Command | What it does |
|---------|-------------|
| `npm run dev` | Start Vite dev server (frontend, port 5173) |
| `./scripts/dev-finnish.sh` | Start FastAPI backend (Linux, port 8001) |
| `.\scripts\run-backend-local.ps1` | Start backend with SQLite (Windows) |
| `.\scripts\run-backend-homelab.ps1` | Start backend connected to homelab DB via Tailscale (Windows) |
| `./scripts/test.sh` | Run all tests (e2e + API) |
| `API_BASE_URL=http://dobbybrain:8001 ./scripts/test.sh` | Run API tests against homelab |

---

## Key Paths

| Path | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/routers/` | API route handlers (exercise, words, health, vocabulary…) |
| `backend/app/services/` | Business logic (spaced repetition, AI, inflections) |
| `backend/app/config.py` | Settings — DB URL, API key, ports |
| `src/App.tsx` | React app entry |
| `src/pages/` | Page components |
| `openclaw-skill/` | OpenClaw Finnish trainer skill |
| `e2e/` | TypeScript Playwright tests (browser/UI) |
| `tests/playwright/` | Python API tests (FastAPI endpoints) |
| `scripts/test.sh` | CI entry point — runs both test suites |

---

## Test Strategy

| Suite | Location | What it tests | Runner |
|-------|----------|--------------|--------|
| e2e (TypeScript) | `e2e/` | Browser UI, page load, responsiveness | `npx playwright test e2e/` |
| API (Python) | `tests/playwright/` | FastAPI endpoints, HTTP status codes, response shapes | `python3 test_*.py` |

### Test Environments

| Environment | API_BASE_URL |
|-------------|-------------|
| Local FastAPI (default) | `http://localhost:8001` |
| Homelab via Tailscale | `http://dobbybrain:8001` |
| Production | `https://ai-vaerksted.cloud/finnish/api` |

### API Test Files

| File | Covers |
|------|--------|
| `test_smoke.py` | `/health`, `/health/simple` |
| `test_api_words.py` | `GET /words`, `POST /words/search`, `POST /words/add` validation |
| `test_api_exercise.py` | `GET /exercise/next`, `GET /exercise/history`, `POST /exercise/result` |

### Adding API Tests

1. Create `tests/playwright/test_api_<scope>.py`
2. Add `sys.path.insert(0, ".")` and `from conftest import API_BASE`
3. Use `urllib.request` for HTTP calls (no browser needed)
4. Add `if __name__ == "__main__":` block with `sys.exit(failures)`
5. Add `python3 test_api_<scope>.py` to `scripts/test.sh`

---

## AI Services

| File | Role |
|------|------|
| `backend/app/services/ai_service.py` | MiniMax/OpenAI client init, definitions, grammatical forms, example sentences |
| `backend/app/services/inflection_service.py` | Generates & stores noun cases (12) and verb forms (16) via LLM |
| `backend/app/config.py` | `minimax_api_key`, `openai_api_key` settings |
| `backend/.env` | Secret keys — not committed |

**Inflection flow:** `POST /api/words/add` → `_add_word_impl()` → `generate_and_store_inflections()` → stores to `app.inflections` / `app.verb_forms`

**MiniMax quirk:** Model returns `<think>…</think>` reasoning blocks before JSON. Both service files have `_extract_json()` that strips these with a regex before parsing.

**Key config:** MiniMax key lives in `backend/.env` as `MINIMAX_API_KEY`. If missing, inflections are silently skipped (returns `{"inflections":0,"verb_forms":0}`).

---

## Database

| Detail | Value |
|--------|-------|
| Engine | PostgreSQL 15 |
| Port | 5433 (homelab) |
| DB | `learning_finnish` |
| User | `learning_finnish` |
| Data | `/mnt/seagate_8TB/finnish/postgres_data/` |
| Docker | `finnish-db` container, `~/homelab/apps/finnish-db/docker-compose.yml` |

---

## CI/CD

- **Single entry point:** `./scripts/test.sh`
- **Exit codes:** 0 = all passed, non-zero = failures
- **Auto-deploy:** Push to `master` → GitHub webhook → VPS rebuilds Docker container
