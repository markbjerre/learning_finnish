# Learning Finnish — Update Summary

**Status:** DB on homelab | Spaced repetition | OpenClaw skill deployed

## Architecture

PostgreSQL on homelab (`dobbybrain:5433` via Tailscale) → FastAPI on VPS. Schema `app` avoids conflict with homelab `public.words`.

## API (Spaced Repetition / OpenClaw)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/exercise/next` | GET | Daily exercise words |
| `/api/exercise/result` | POST | Submit scores |
| `/api/words`, `/api/words/add` | GET/POST | List, add words |
| `/api/words/bulk-add` | POST | Bulk add |
| `/api/concepts` | GET/POST | Concepts |
| `/api/settings` | GET/PUT | Level, word count |
| `/api/stats` | GET | Dashboard stats |

**Traefik:** Frontend must NOT catch `/finnish` — Finnish traffic goes to `ai-vaerksted-finnish` only (405 fix).

## Scripts

```bash
python scripts/test_db_and_api.py --db-only    # DB test
python scripts/seed_data.py                    # Seed (PostgreSQL)
python backend/scripts/migrate_spaced_repetition.py  # Migration
```

## Homelab DB

- **Path:** `/mnt/seagate_8TB/finnish/postgres_data`
- **Compose:** `$HOME/homelab/apps/finnish-db/` (on homelab)
- **VPS:** `DATABASE_URL=postgresql+asyncpg://...@dobbybrain:5433/learning_finnish`

## Reference

- `Spaced_repetition_instruction.md` — Spec
- `Full_finnish_openclaw_plan.md` — Architecture
- `finnish_2_0_instructions.md` — DB + Tailscale setup
- `homelab/DEPLOY_VPS_FASTAPI.md` — VPS runbook
- `DobbyBrain/192.168.0.252-control/` — Homelab reference
