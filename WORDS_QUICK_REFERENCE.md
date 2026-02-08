# Word Lookup Feature - Quick Reference

## New Files

```
backend/
├── app/
│   ├── models_db.py (updated)
│   │   ├── Word model
│   │   ├── UserWord model
│   │   └── WordStatusEnum
│   ├── models/__init__.py (updated)
│   │   └── Added Word/UserWord Pydantic schemas
│   ├── services/
│   │   └── ai_service.py (NEW)
│   │       └── AI-powered definitions and examples
│   ├── routers/
│   │   └── words.py (NEW)
│   │       └── 6 word lookup/dictionary endpoints
│   └── main.py (updated)
│       └── Registered words router
├── requirements.txt (updated)
│   └── Added openai==1.3.0
└── WORDS_API_DOCUMENTATION.md (NEW)
    └── Complete API reference
```

## Database Schema

```sql
-- Words dictionary table
CREATE TABLE words (
    id VARCHAR(255) PRIMARY KEY,
    finnish_word VARCHAR(255) UNIQUE NOT NULL,
    english_translation VARCHAR(255) NOT NULL,
    part_of_speech VARCHAR(100),
    grammatical_forms TEXT,              -- JSON
    example_sentences TEXT,              -- JSON
    ai_definition TEXT,
    ai_examples TEXT,                    -- JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- User word tracking table
CREATE TABLE user_words (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    word_id VARCHAR(255) NOT NULL,
    status VARCHAR(50),                  -- recent, learning, mastered
    proficiency INTEGER DEFAULT 0,       -- 0-100
    date_added TIMESTAMP,
    last_reviewed TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);
```

## API Endpoints

| Method | URL | Input | Output |
|--------|-----|-------|--------|
| POST | `/api/words/search?finnish_word=X` | Finnish word | WordSearchResult |
| POST | `/api/words/save` | SaveWordRequest | UserWord |
| GET | `/api/words/user-words/{user_id}` | User ID, optional: status, limit, offset | List[UserWord] |
| PUT | `/api/words/{word_id}/status/{user_id}` | UpdateWordStatusRequest | UserWord |
| GET | `/api/words/{word_id}/ai-definition` | Word ID | Dict with definition |
| DELETE | `/api/words/{word_id}/{user_id}` | Word & User IDs | Success message |

## Request/Response Examples

### Search Word
```bash
POST /api/words/search?finnish_word=kissa
Response: {
  "finnish_word": "kissa",
  "english_translation": "cat",
  "part_of_speech": "noun",
  "grammatical_forms": [...],
  "example_sentences": [...],
  "ai_definition": "..."
}
```

### Save Word
```bash
POST /api/words/save
Body: {
  "finnish_word": "kissa",
  "user_id": "user-123"
}
Response: {
  "id": "user-word-456",
  "user_id": "user-123",
  "word_id": "word-123",
  "status": "recent",
  "proficiency": 0,
  "date_added": "2024-01-15T10:30:00",
  ...
}
```

### Get User Words
```bash
GET /api/words/user-words/user-123?status=learning&limit=20
Response: [
  { UserWord object },
  { UserWord object },
  ...
]
```

### Update Word Status
```bash
PUT /api/words/word-123/status/user-123
Body: {
  "status": "learning",
  "proficiency": 65
}
Response: {
  ...updated UserWord...
}
```

## AI Service

**Module:** `app/services/ai_service.py`

**Methods:**
- `await ai_service.get_word_definition(finnish_word)` - Get English definition
- `await ai_service.get_grammatical_forms(finnish_word)` - Get cases
- `await ai_service.get_example_sentences(finnish_word)` - Get examples

**Features:**
- Uses OpenAI API if OPENAI_API_KEY is set
- Falls back to mock data if unavailable
- Caches results in database
- Returns realistic mock data for unknown words

**Mock Data Words:**
kissa, kirja, vesi, koulu, ystävä, kauneus, mies, nainen, talo, puu

## Configuration

**.env file:**
```env
OPENAI_API_KEY=sk-...                          # Optional
DATABASE_URL=postgresql+asyncpg://...          # PostgreSQL URL
ENABLE_AI_PRACTICE=true                        # Feature flag
```

**Settings in app/config.py:**
```python
openai_api_key: Optional[str] = None
enable_ai_practice: bool = False
```

## Testing

### Check Syntax
```bash
python -m py_compile app/models_db.py app/routers/words.py app/services/ai_service.py
```

### Start Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Test Endpoints
```bash
# Search
curl -X POST "http://localhost:8001/api/words/search?finnish_word=kissa"

# Save
curl -X POST "http://localhost:8001/api/words/save" \
  -H "Content-Type: application/json" \
  -d '{"finnish_word": "kissa", "user_id": "test-user"}'

# Get words
curl "http://localhost:8001/api/words/user-words/test-user"

# Update status
curl -X PUT "http://localhost:8001/api/words/word-id/test-user" \
  -H "Content-Type: application/json" \
  -d '{"status": "learning", "proficiency": 50}'
```

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Word Learning Status Flow

```
recent (just added)
    ↓
learning (actively studying)
    ↓
mastered (fully learned)
```

Each status can track:
- Date when status changed
- Proficiency score (0-100)
- Review count (how many times reviewed)
- Last review timestamp

## Proficiency Scoring

Proficiency ranges from 0 to 100:
- **0-20**: Just learned (recent)
- **21-60**: Learning (requires more practice)
- **61-85**: Nearly mastered
- **86-100**: Mastered (expert level)

## Data Models Summary

```python
# Database Model
class Word:
    id: str (PK)
    finnish_word: str (UNIQUE)
    english_translation: str
    part_of_speech: str
    grammatical_forms: JSON
    example_sentences: JSON
    ai_definition: str
    ai_examples: JSON

class UserWord:
    id: str (PK)
    user_id: str (FK)
    word_id: str (FK)
    status: enum(recent, learning, mastered)
    proficiency: int (0-100)
    date_added: datetime
    last_reviewed: datetime
    review_count: int

# API Models (Pydantic)
class Word(BaseModel)
class UserWord(BaseModel)
class GrammaticalForm(BaseModel)
class ExampleSentence(BaseModel)
class WordSearchResult(BaseModel)
class SaveWordRequest(BaseModel)
class UpdateWordStatusRequest(BaseModel)
```

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Word found and returned |
| 201 | Created | New word saved to wordbook |
| 204 | No Content | Operation successful but no body |
| 400 | Bad Request | Invalid status value or missing parameters |
| 404 | Not Found | Word not found in wordbook |
| 500 | Server Error | Database or API error |

## Common Tasks

### Add a word to user's wordbook
```python
await db.execute(
    select(UserWord).where(
        (UserWord.user_id == user_id) &
        (UserWord.word_id == word_id)
    )
)
```

### Get all learning words
```python
GET /api/words/user-words/user-123?status=learning
```

### Update multiple word statuses
```python
# Loop through words and call:
PUT /api/words/{word_id}/status/{user_id}
```

### Search for word and add if not exists
```python
# 1. POST /api/words/search?finnish_word=X
# 2. If not found, POST /api/words/save with word
# 3. Word and definitions auto-created
```

## Integration Checklist

- [ ] Database migration runs (creates words and user_words tables)
- [ ] OpenAI API key configured (or will use mock data)
- [ ] requirements.txt installed (openai package)
- [ ] Backend starts without errors
- [ ] /api/words/search endpoint works
- [ ] /api/words/save endpoint works
- [ ] /api/words/user-words/{user_id} endpoint works
- [ ] /api/words/{word_id}/status/{user_id} endpoint works
- [ ] Swagger UI shows word endpoints at http://localhost:8001/docs
- [ ] Mock data works when OpenAI API unavailable

## Files Reference

| File | Purpose | Changes |
|------|---------|---------|
| app/models_db.py | Database models | Added Word, UserWord classes |
| app/models/__init__.py | Pydantic schemas | Added Word*, UserWord* schemas |
| app/services/ai_service.py | AI logic | NEW - Complete file |
| app/routers/words.py | API endpoints | NEW - Complete file |
| app/main.py | App setup | Added words router import/registration |
| requirements.txt | Dependencies | Added openai==1.3.0 |

## Performance Tips

1. Use pagination with limit/offset for large wordbooks
2. Filter by status to reduce result set size
3. Cache word definitions in the database (automatic)
4. Use indexed finnish_word column for fast lookups
5. Use selectinload to eagerly load related word data

## Debugging

### Check if AI service working
```python
from app.services.ai_service import ai_service
definition = await ai_service.get_word_definition("kissa")
print(definition)
```

### Check database connection
```python
from app.database import async_session
async with async_session() as session:
    result = await session.execute(select(Word))
    words = result.scalars().all()
    print(f"Found {len(words)} words")
```

### Enable debug logging
```python
logging.basicConfig(level=logging.DEBUG)
```

## Support Documentation

For complete details, see:
- `WORDS_API_DOCUMENTATION.md` - Full API reference
- `WORD_LOOKUP_IMPLEMENTATION.md` - Implementation details
- Code docstrings - Function documentation
- Type hints - Parameter and return types
