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
| `npm run dev` | Start Vite dev server (frontend only, port 5173) |
| `cd backend && python app.py` | Start Flask dev server (backend only, port 8000) |
| `docker build -t learning-finnish . && docker run -p 8000:8000 learning-finnish` | Full stack (Docker) |
| `./scripts/test.sh` | Run all Playwright tests (default: localhost:8000) |
| `TEST_BASE_URL=https://ai-vaerksted.cloud/finnish ./scripts/test.sh` | Run tests against production |

---

## Key Paths

| Path | Purpose |
|------|---------|
| `backend/app.py` | Flask app — static serving + API endpoints |
| `backend/prompts/` | Prompt builders (not yet wired to endpoints) |
| `src/App.tsx` | Main React component |
| `tests/playwright/conftest.py` | Shared BASE_URL config |
| `tests/playwright/test_smoke.py` | Page load + API health tests |
| `tests/playwright/test_frontend.py` | React rendering tests |
| `tests/playwright/test_routing.py` | SPA fallback + static file tests |
| `tests/playwright/test_performance.py` | Load time + asset size tests |
| `scripts/test.sh` | CI test runner — single entry point |
| `vite.config.ts` | Vite config — base MUST stay `/finnish/` |
| `Dockerfile` | Root multi-stage build (frontend + backend) |

---

## Test Environments

| Environment | TEST_BASE_URL |
|-------------|--------------|
| Docker local (default) | `http://localhost:8000` |
| Vite dev server | `http://localhost:5173` |
| Production | `https://ai-vaerksted.cloud/finnish` |

---

## CI/CD

- **Single entry point:** `./scripts/test.sh`
- **Exit codes:** 0 = all passed, non-zero = failures (CI-compatible)
- **No interactive prompts** — all tests run headless
- **Selective run:** `cd tests/playwright && python test_smoke.py` for a single suite
- **Auto-deploy:** Push to `main` → GitHub webhook → VPS rebuilds Docker container automatically

---

## Adding New Tests

1. Create `tests/playwright/test_<scope>.py`
2. Add `sys.path.insert(0, ".")` and `from conftest import BASE_URL, API_BASE`
3. Add `if __name__ == "__main__":` block with `sys.exit(failures)`
4. Add `python test_<scope>.py` line to `scripts/test.sh`
5. Add entry to `docs/INDEX.md` test files table
