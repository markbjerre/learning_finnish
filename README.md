# Learning Finnish

AI-powered Finnish language learning application.

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** FastAPI
- **Database:** PostgreSQL (homelab, via Tailscale)

## Database

PostgreSQL runs on the homelab (192.168.0.252) at `/mnt/seagate_8TB/finnish/postgres_data`. The VPS connects via Tailscale at `dobbybrain:5433`.

**Connection string (VPS):**
```
DATABASE_URL=postgresql+asyncpg://learning_finnish:PASSWORD@dobbybrain:5433/learning_finnish
```

## Documentation

- **UPDATE_SUMMARY.md** — Deployment status, credentials, connection details
- **finnish_2_0_instructions.md** — Original migration + SSH tunnel plan (Tailscale used instead)
- **homelab/** — Homelab deployment files (docker-compose, schema, Tailscale, DuckDNS)
- **CLAUDE_DEV.md** — Development guide

## Live

https://ai-vaerksted.cloud/finnish
