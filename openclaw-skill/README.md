# OpenClaw Finnish Trainer Skill

Daily Finnish exercises with spaced repetition. OpenClaw calls the Learning Finnish API (`ai-vaerksted-finnish:8000` on VPS).

**Status:** Deployed — live on OpenClaw. See `CLAUDE.md` and `DobbyBrain/CONTENTS.md` for full project docs.

## Install

Copy this folder to your OpenClaw skills directory:

```bash
cp -r openclaw-skill/finnish-trainer ~/.openclaw/skills/
```

Or on Windows:

```powershell
Copy-Item -Recurse openclaw-skill\finnish-trainer $env:USERPROFILE\.openclaw\skills\
```

## Prerequisites

1. Learning Finnish API running (VPS or local)
2. OpenClaw configured with HTTP tool pointing at the API
3. Set `FINNISH_API_KEY` in API `.env` if using auth
4. Configure OpenClaw to send `Authorization: Bearer {key}` when calling the API

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill definition, triggers, API usage |
| `generate.md` | Prompt for generating exercise sentences |
| `score.md` | Prompt for scoring user responses |
| `TEST_PROMPT.md` | Full API test + seed prompt (20 words, 3 concepts) |

## API Endpoints Used

- `GET /api/health/simple` — health check
- `GET /api/exercise/next` — fetch words + concepts for today
- `POST /api/exercise/result` — submit scores after user replies
- `POST /api/words` or `POST /api/words/add` — add single word
- `POST /api/words/bulk-add` — bulk add words (rows or csv)
- `GET /api/words` — list words
- `POST /api/concepts` — create concept
- `GET /api/concepts` — list concepts

## Full Test

Send the prompt from `finnish-trainer/TEST_PROMPT.md` to OpenClaw to seed the database and verify all endpoints.
