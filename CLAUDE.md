# Learning Finnish — Claude Configuration

## Type
Mixed

## Entry points
| Action | Command |
|--------|---------|
| **Main entry** | `backend/app.py` (FastAPI) + `src/` (React frontend) |
| **Run locally** | `./scripts/dev-finnish.sh` (Linux) or `.\scripts\run-backend-local.ps1` (SQLite) or `.\scripts\run-backend-homelab.ps1` (homelab via Tailscale) — backend :8001 |
| **Run tests** | `./scripts/test.sh` or `npm run build` |

## Documentation
See [docs/INDEX.md](docs/INDEX.md). Do not create new docs without updating INDEX.

## Overview
React + FastAPI Finnish learning app with spaced repetition. OpenClaw skill for daily exercises. See root CLAUDE.md for workspace conventions.

## Key Files
- **Index:** docs/PROJECT_INDEX.md — design components, quick reference
- **Backend:** backend/ — FastAPI, PostgreSQL
- **OpenClaw skill:** openclaw-skill/finnish-trainer/SKILL.md
