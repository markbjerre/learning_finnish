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
See [docs/INDEX.md](docs/INDEX.md). Do not create new docs without updating INDEX.

## Overview
React + FastAPI Finnish learning app with spaced repetition. OpenClaw skill for daily exercises. See root CLAUDE.md for workspace conventions.

## Key Files
- **Architecture:** docs/PROJECT_INDEX.md — current system overview
- **Backend services:** `backend/app/services/` — spaced repetition, AI (MiniMax), inflections
- **Config/env:** `backend/app/config.py` + `backend/.env` — DB, `MINIMAX_API_KEY`, ports
- **OpenClaw skill:** `openclaw-skill/finnish-trainer/SKILL.md`
- **API docs:** `backend/WORDS_API_DOCUMENTATION.md`

## AI / Inflections
- MiniMax API (`MINIMAX_API_KEY` in `backend/.env`) generates inflections when words are added
- Uses OpenAI-compatible client pointed at `https://api.minimax.io/v1` with model `MiniMax-M2.5`
- MiniMax returns `<think>…</think>` blocks — `_extract_json()` in both service files strips these
- Nouns/adjectives → 12 Finnish cases stored in `app.inflections`
- Verbs → 16 conjugation forms stored in `app.verb_forms`
- Falls back to OpenAI if `OPENAI_API_KEY` set, then mock data if neither key present
