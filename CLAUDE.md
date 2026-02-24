---
type: Web app (React + Flask skeleton)
---

# Learning Finnish — Project Context

## Entry Points

| Command | Purpose | Details |
|---------|---------|---------|
| `npm run dev` | Frontend dev server | Vite on :5173, hot reload enabled |
| `docker build -t learning-finnish . && docker run -p 8000:8000 learning-finnish` | Full stack Docker | Multi-stage Vite build → Flask/gunicorn on :8000 |
| `./scripts/test.sh` | Run all Playwright tests | Against local dev (http://localhost:8000) |
| `TEST_BASE_URL=https://ai-vaerksted.cloud/finnish ./scripts/test.sh` | Run tests against production | Test live environment |

## Architecture

React SPA built by Vite → served as static files by Flask/gunicorn → Traefik strips `/finnish` prefix → Docker multi-stage build.

- **Frontend:** React 18 + Vite, builds to `backend/static/dist/`
- **Backend:** Flask with gunicorn, serves compiled React + dynamic API endpoints
- **Proxy:** Traefik strips `/french` path prefix before request reaches Flask
- **Build:** Multi-stage Dockerfile: Node build stage → Python runtime stage
- **Deployment:** VPS, auto-triggered via GitHub webhook on push to main

## Key Paths

| Path | Purpose |
|------|---------|
| `backend/app.py` | Flask app, static file serving, health endpoints |
| `backend/prompts/` | Prompt builders (`word_lookup.py`, `translation.py`), not yet wired to endpoints |
| `src/App.tsx` | Main React component, renders skeleton heading |
| `tests/playwright/` | Playwright test suite (smoke, frontend, routing, performance) |
| `scripts/test.sh` | CI test runner, invokes Playwright |
| `vite.config.ts` | Vite config, base MUST be `/finnish/` (Traefik path stripping) |
| `Dockerfile` | Root multi-stage build, Node + Python |
| `backend/Dockerfile` | Backend-only build (alternative) |

## Testing

Playwright tests use `TEST_BASE_URL` environment variable to target different environments:

```bash
# Local dev (default)
./scripts/test.sh

# Explicit local dev
TEST_BASE_URL=http://localhost:8000 ./scripts/test.sh

# Staging
TEST_BASE_URL=https://staging.example.com/finnish ./scripts/test.sh

# Production
TEST_BASE_URL=https://ai-vaerksted.cloud/finnish ./scripts/test.sh
```

Test files:
- `tests/playwright/test_smoke.py` — Page load, health endpoints
- `tests/playwright/test_frontend.py` — React rendering, DOM elements
- `tests/playwright/test_routing.py` — SPA fallback, static file serving, JSON responses
- `tests/playwright/test_performance.py` — Load times, asset sizes

## Deployment

**Auto-deploy:** Push to `main` branch → GitHub webhook → VPS rebuilds Docker container → live at `https://ai-vaerksted.cloud/finnish`

**Manual deploy:**
```bash
docker build -t learning-finnish .
docker run -p 8000:8000 learning-finnish
```

Traefik routes `/finnish/*` prefix to container port 8000; Vite's base `/finnish/` aligns with this prefix stripping.

## Known Issues

1. **Unused prompts:** `backend/prompts/word_lookup.py` contains `build_word_lookup_prompt()` and `build_translation_prompt()` functions not wired to any API endpoint.

2. **Vite base path:** `vite.config.ts` has `base: '/finnish/'` for Traefik compatibility. Do not change to `/` without updating reverse proxy.

## Documentation

Full documentation index: [docs/INDEX.md](docs/INDEX.md)
