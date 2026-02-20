# Full Finnish API Test Prompt

Use this prompt with OpenClaw to seed the database and exercise all API endpoints.

---

**Run a full Finnish API test: seed the database and exercise all endpoints**

1. **Health check** — `GET http://ai-vaerksted-finnish:8000/api/health/simple` — confirm API is up.

2. **Bulk add 20 words** — `POST http://ai-vaerksted-finnish:8000/api/words/bulk-add` with body:
```json
{
  "rows": [
    ["talo", "hus", "house", "noun"],
    ["kissa", "kat", "cat", "noun"],
    ["koira", "hund", "dog", "noun"],
    ["kirja", "bog", "book", "noun"],
    ["vesi", "vand", "water", "noun"],
    ["ruoka", "mad", "food", "noun"],
    ["ystävä", "ven", "friend", "noun"],
    ["perhe", "familie", "family", "noun"],
    ["työ", "arbejde", "work", "noun"],
    ["aika", "tid", "time", "noun"],
    ["olla", "være", "to be", "verb"],
    ["tehdä", "gøre", "to do", "verb"],
    ["tulla", "komme", "to come", "verb"],
    ["mennä", "gå", "to go", "verb"],
    ["nähdä", "se", "to see", "verb"],
    ["iso", "stor", "big", "adjective"],
    ["pieni", "lille", "small", "adjective"],
    ["hyvä", "god", "good", "adjective"],
    ["uusi", "ny", "new", "adjective"],
    ["kaunis", "smuk", "beautiful", "adjective"]
  ]
}
```

3. **Add 3 concepts** — `POST http://ai-vaerksted-finnish:8000/api/concepts` for each:
   - `{"name": "Nominatiivi", "description": "Subjektskasus – hvem/hvad gør handlingen", "tags": ["kasus", "grammatik"]}`
   - `{"name": "Genetiivi", "description": "Ejefald – hvem/hvad noget tilhører", "tags": ["kasus", "grammatik"]}`
   - `{"name": "Partitiivi", "description": "Delvis objekt – ubestemt mængde eller del af noget", "tags": ["kasus", "grammatik"]}`

4. **List words** — `GET http://ai-vaerksted-finnish:8000/api/words?limit=25` — confirm 20 words exist.

5. **List concepts** — `GET http://ai-vaerksted-finnish:8000/api/concepts` — confirm 3 concepts exist.

6. **Get next exercise** — `GET http://ai-vaerksted-finnish:8000/api/exercise/next` — note returned `words`, `concepts`, `level`.

7. **Submit sample result** — `POST http://ai-vaerksted-finnish:8000/api/exercise/result` with body (replace `WORD_ID_1`, `WORD_ID_2`, `CONCEPT_ID_1` with IDs from step 6):
```json
{
  "exercise_type": "translation",
  "prompt_sent": "Talo on iso. Kissa on pieni.",
  "user_response": "Huset er stort. Katten er lille.",
  "ai_feedback": "Godt gået! Husk partitiivi ved ubestemt mængde.",
  "word_scores": [
    {"word_id": "WORD_ID_1", "score": 8, "feedback": "Korrekt"},
    {"word_id": "WORD_ID_2", "score": 7, "feedback": "Lille fejl i ordstilling"}
  ],
  "concept_scores": [
    {"concept_id": "CONCEPT_ID_1", "score": 6, "feedback": "Nominatiivi brugt korrekt"}
  ]
}
```

8. **Summarize** — Report: health status, words created, concepts created, exercise response, result submission status.
