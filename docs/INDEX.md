# Learning Finnish — Documentation Index

Single source of truth for all project docs. Before creating a new doc, check here first.

## Main Documentation

| Doc | When to read | Path |
|-----|-------------|------|
| CLAUDE.md | Project context, architecture, key paths, known issues | ../CLAUDE.md |
| AGENTS.md | Session start, run commands, test environments, CI/CD | ../AGENTS.md |
| README.md | Quick overview | ../README.md |
| DEPLOYMENT.md | Deployment instructions, Docker, Traefik, webhook | ../DEPLOYMENT.md |
| Deployment_Instructions_v2.md | Detailed step-by-step deployment | ../Deployment_Instructions_v2.md |
| SPEED_ANALYSIS.md | Performance analysis | ../SPEED_ANALYSIS.md |

## Test Files

| File | Scope |
|------|-------|
| tests/playwright/test_smoke.py | Page load, API health |
| tests/playwright/test_frontend.py | React rendering, DOM elements |
| tests/playwright/test_routing.py | SPA fallback, static files, JSON format |
| tests/playwright/test_performance.py | Load time, response time, asset size |
