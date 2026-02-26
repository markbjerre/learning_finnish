---
name: Finnish Trainer
description: Daily Finnish language exercises with AI scoring and spaced repetition
triggers:
  - finnish exercise
  - suomi
  - finnish drill
  - add finnish word
---

# Finnish Trainer

## Overview

Generates Finnish language exercises, scores responses, and manages vocabulary through a spaced repetition system. Integrates with the Learning Finnish API.

**Main user:** `user-main-admin` (Mark). Always pass this as `user_id` when submitting exercise results.

## API Endpoints (Full URLs)

Base: `http://ai-vaerksted-finnish:8000` (OpenClaw and Finnish share Docker network)

**IMPORTANT: Use these exact full URLs. The path must include `/api`.**

| Action | Method | Full URL |
|--------|--------|----------|
| Get next exercise words | GET | `http://ai-vaerksted-finnish:8000/api/exercise/next` |
| Submit exercise result | POST | `http://ai-vaerksted-finnish:8000/api/exercise/result` |
| List all concepts | GET | `http://ai-vaerksted-finnish:8000/api/concepts` |
| List concepts with mastery | GET | `http://ai-vaerksted-finnish:8000/api/concepts?user_id=user-main-admin` |
| Add word (any language) | POST | `http://ai-vaerksted-finnish:8000/api/words` |
| Bulk add words | POST | `http://ai-vaerksted-finnish:8000/api/words/bulk-add` |
| List words | GET | `http://ai-vaerksted-finnish:8000/api/words` |
| Health check | GET | `http://ai-vaerksted-finnish:8000/api/health/simple` |

## Auth

When `FINNISH_API_KEY` is set on the API server, all requests need header:
`Authorization: Bearer {FINNISH_API_KEY}`. Health endpoints are exempt.

## Daily Exercise Flow

Words and concepts are fetched **separately** — concepts rotate weekly, words rotate daily.

1. **Fetch words**: `GET /api/exercise/next` → receives words (with inflections) + level
2. **Fetch active concepts**: `GET /api/concepts?user_id=user-main-admin` → pick 1-3 concepts to focus on this week (see concept selection below)
3. Generate 2-3 sentences using those words + active concepts (use `generate.md`)
4. Send to user on WhatsApp
5. When user replies, score their response (use `score.md`)
6. **POST** `/api/exercise/result` with `user_id`, `word_scores`, and `concept_scores`

### Exercise result body
```json
{
  "exercise_type": "translation",
  "user_id": "user-main-admin",
  "prompt_sent": "...",
  "user_response": "...",
  "ai_feedback": "...",
  "word_scores": [{"word_id": "...", "score": 8, "feedback": "..."}],
  "concept_scores": [{"concept_id": "...", "score": 7, "feedback": "..."}]
}
```

## Concept Selection (Weekly Rotation)

You manage which concepts are active — the API does not. Strategy:

1. Fetch all concepts with mastery: `GET /api/concepts?user_id=user-main-admin`
2. Filter to concepts with `frequency >= 3` first (common in everyday Finnish)
3. Prefer concepts where `mastery < 7.0` (not yet near-mastered)
4. Pick 1-3 concepts. Suggested count by situation:
   - Early session (mastery < 2): 1 concept at a time
   - Normal session: 2 concepts
   - Review session: 3 concepts from different categories (case + verb + other)
5. Keep the same concepts for ~7 days (track the rotation date yourself), then rotate

**Concept response fields:**
```json
{
  "id": "concept-03",
  "name": "Partitive case",
  "name_fi": "Partitiivi",
  "frequency": 5,
  "difficulty": 4,
  "mastery": 2.40,
  "exercise_count": 24
}
```
- `frequency` 1-5: how often this appears in real Finnish (5 = daily use)
- `difficulty` 1-5: how hard to master
- `mastery` 0-10: user's XP bar; grows `+0.01 × score` per exercise (~100-1000 exercises to 10.0)

## Adding Words

When the user wants to add a word — accepts Finnish, Danish, or English input:

1. **POST** to `http://ai-vaerksted-finnish:8000/api/words`
   - Content-Type: application/json
   - Body: `{"word": "hund"}` — API normalizes language, finds Finnish lemma, generates inflections
   - Or with hint: `{"word": "hund", "source_lang": "da"}`
2. API auto-detects language, translates to Finnish, lemmatizes, detects word type
3. Inflections are auto-generated
4. Confirm to user: "Tilføjet [finnish_word] ([english]) med [N] inflektioner"

If word is invalid or misspelled, API returns `{"status": "invalid", "error": "..."}` — tell the user.

## Exercise Generation Rules

- Use the level from the API response (e.g. 15/100) to calibrate difficulty
- Level 1-20: very simple sentences, basic vocabulary, present tense
- Level 21-40: compound sentences, past tense, common cases
- Level 41-60: complex grammar, rarer cases, varied tenses
- Level 61-80: nuanced expression, idioms, conditional
- Level 81-100: near-native complexity

## Scoring Rules

- Score each word 0-10
- Score each active concept 0-10
- Consider: correct case/kasus, spelling, word order, verb form
- Provide feedback in Danish
- Return structured JSON only (see `score.md`)

## Cron Setup

```bash
openclaw cron add --schedule "0 7 * * *" --message "Run the Finnish trainer daily exercise"
```
