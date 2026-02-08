# Word Lookup and Dictionary API Documentation

## Overview

The Learning Finnish API now includes comprehensive word lookup and dictionary features that allow users to search for words, save them to their personal wordbook, and track their learning progress. The system includes AI-powered definitions and grammatical analysis through OpenAI integration (with automatic fallback to mock data).

## Features

- **Word Search**: Search for Finnish words and get translations, grammatical forms, and example sentences
- **User Wordbook**: Save words to your personal wordbook and organize them
- **Learning Status Tracking**: Track word mastery with status levels (Recent, Learning, Mastered) and proficiency scores
- **AI-Powered Definitions**: Get AI-generated definitions and contextual examples (with mock data fallback)
- **Grammatical Forms**: Access complete grammatical cases for Finnish words
- **Example Sentences**: Learn words in context with realistic sentence examples

## Database Models

### Word Model
Stores dictionary words with complete metadata:
- `id`: Unique identifier
- `finnish_word`: The Finnish word (unique)
- `english_translation`: English translation
- `part_of_speech`: Word category (noun, verb, adjective, etc.)
- `grammatical_forms`: JSON array of grammatical cases
- `example_sentences`: JSON array of example sentences
- `ai_definition`: AI-generated definition
- `ai_examples`: AI-generated example sentences
- `created_at`, `updated_at`: Timestamps

### UserWord Model
Tracks individual user's learning progress for words:
- `id`: Unique identifier
- `user_id`: Reference to user
- `word_id`: Reference to word
- `status`: Learning status (recent, learning, mastered)
- `proficiency`: Proficiency score (0-100)
- `date_added`: When word was added to wordbook
- `last_reviewed`: Last time word was reviewed
- `review_count`: Number of times word was reviewed
- `created_at`, `updated_at`: Timestamps

## API Endpoints

### 1. Search Word
```
POST /api/words/search?finnish_word={word}
```

Search for a Finnish word and get its translation with metadata.

**Query Parameters:**
- `finnish_word` (string, required): The Finnish word to search for

**Response:** `WordSearchResult`
```json
{
  "id": "word-123",
  "finnish_word": "kissa",
  "english_translation": "cat",
  "part_of_speech": "noun",
  "grammatical_forms": [
    {
      "case": "nominative",
      "finnish": "kissa",
      "english": "cat"
    },
    {
      "case": "genitive",
      "finnish": "kissan",
      "english": "of the cat"
    }
  ],
  "example_sentences": [
    {
      "finnish": "Minulla on kissa nimeltä Mirri.",
      "english": "I have a cat named Mirri."
    }
  ],
  "ai_definition": "A small domesticated carnivorous mammal..."
}
```

**Error Responses:**
- `400`: Missing or invalid finnish_word parameter
- `500`: Server error

---

### 2. Save Word to Wordbook
```
POST /api/words/save
```

Save a word to the user's personal wordbook.

**Request Body:** `SaveWordRequest`
```json
{
  "finnish_word": "kissa",
  "user_id": "user-123"
}
```

**Response:** `UserWord`
```json
{
  "id": "user-word-456",
  "user_id": "user-123",
  "word_id": "word-123",
  "word": {
    "id": "word-123",
    "finnish_word": "kissa",
    "english_translation": "cat",
    "part_of_speech": "noun",
    ...
  },
  "status": "recent",
  "proficiency": 0,
  "date_added": "2024-01-15T10:30:00",
  "review_count": 0
}
```

**Error Responses:**
- `404`: User not found
- `400`: Invalid request body
- `500`: Server error

**Behavior:**
- If the word doesn't exist in the database, it will be created with AI-generated definitions and examples
- If the user already has the word saved, it returns the existing entry without duplicating

---

### 3. Get User's Saved Words
```
GET /api/words/user-words/{user_id}?status={status}&limit={limit}&offset={offset}
```

Retrieve all words saved by a specific user with optional filtering.

**Path Parameters:**
- `user_id` (string, required): The user ID

**Query Parameters:**
- `status` (string, optional): Filter by status - `recent`, `learning`, or `mastered`
- `limit` (integer, optional): Number of results (1-1000, default: 100)
- `offset` (integer, optional): Number of results to skip (default: 0)

**Response:** List of `UserWord` objects
```json
[
  {
    "id": "user-word-456",
    "user_id": "user-123",
    "word_id": "word-123",
    "word": {...},
    "status": "learning",
    "proficiency": 45,
    "date_added": "2024-01-15T10:30:00",
    "last_reviewed": "2024-01-20T14:22:00",
    "review_count": 5
  },
  {
    "id": "user-word-789",
    "user_id": "user-123",
    "word_id": "word-124",
    "word": {...},
    "status": "mastered",
    "proficiency": 95,
    "date_added": "2024-01-10T09:15:00",
    "last_reviewed": "2024-01-21T16:45:00",
    "review_count": 12
  }
]
```

**Error Responses:**
- `404`: User not found
- `400`: Invalid status value
- `500`: Server error

---

### 4. Update Word Status
```
PUT /api/words/{word_id}/status/{user_id}
```

Update a word's status and proficiency level for a user.

**Path Parameters:**
- `word_id` (string, required): The word ID
- `user_id` (string, required): The user ID

**Request Body:** `UpdateWordStatusRequest`
```json
{
  "status": "learning",
  "proficiency": 65
}
```

**Response:** `UserWord`
```json
{
  "id": "user-word-456",
  "user_id": "user-123",
  "word_id": "word-123",
  "word": {...},
  "status": "learning",
  "proficiency": 65,
  "date_added": "2024-01-15T10:30:00",
  "last_reviewed": "2024-01-21T17:00:00",
  "review_count": 6
}
```

**Error Responses:**
- `404`: Word not found in user's wordbook
- `400`: Invalid status value
- `500`: Server error

**Behavior:**
- Automatically updates `last_reviewed` timestamp
- Increments `review_count`
- Proficiency is clamped to 0-100 range
- Valid statuses: `recent`, `learning`, `mastered`

---

### 5. Get AI Definition
```
GET /api/words/{word_id}/ai-definition
```

Get AI-powered definition and contextual examples for a word.

**Path Parameters:**
- `word_id` (string, required): The word ID

**Response:** Dictionary with AI content
```json
{
  "word_id": "word-123",
  "finnish_word": "kissa",
  "ai_definition": "A small domesticated carnivorous mammal with soft fur, whiskers, and retractable claws.",
  "ai_examples": [
    {
      "finnish": "Minulla on kissa nimeltä Mirri.",
      "english": "I have a cat named Mirri."
    },
    {
      "finnish": "Kissa istuu ikkunalla.",
      "english": "The cat sits by the window."
    }
  ]
}
```

**Error Responses:**
- `404`: Word not found
- `500`: Server error (or API error if OpenAI fails)

**Behavior:**
- If AI definition doesn't exist, it will be generated on first request
- If OpenAI API is unavailable, mock data will be returned
- Results are cached in the database for future requests

---

### 6. Remove Word from Wordbook
```
DELETE /api/words/{word_id}/{user_id}
```

Remove a word from the user's wordbook.

**Path Parameters:**
- `word_id` (string, required): The word ID
- `user_id` (string, required): The user ID

**Response:** Success message
```json
{
  "status": "success",
  "message": "Word removed from wordbook"
}
```

**Error Responses:**
- `404`: Word not found in user's wordbook
- `500`: Server error

---

## Data Models (Pydantic)

### GrammaticalForm
```python
class GrammaticalForm(BaseModel):
    case: str              # nominative, genitive, partitive, etc.
    finnish: str           # The Finnish form
    english: str           # English translation
```

### ExampleSentence
```python
class ExampleSentence(BaseModel):
    finnish: str           # Example in Finnish
    english: str           # English translation
```

### Word
```python
class Word(BaseModel):
    id: Optional[str]
    finnish_word: str
    english_translation: str
    part_of_speech: str
    grammatical_forms: Optional[List[GrammaticalForm]]
    example_sentences: Optional[List[ExampleSentence]]
    ai_definition: Optional[str]
    ai_examples: Optional[List[ExampleSentence]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

### WordSearchResult
```python
class WordSearchResult(BaseModel):
    id: Optional[str]
    finnish_word: str
    english_translation: str
    part_of_speech: str
    grammatical_forms: Optional[List[GrammaticalForm]]
    example_sentences: Optional[List[ExampleSentence]]
    ai_definition: Optional[str]
```

### UserWord
```python
class UserWord(BaseModel):
    id: Optional[str]
    user_id: str
    word_id: str
    word: Optional[Word]              # Nested word data
    status: WordStatus                # recent, learning, mastered
    proficiency: int                  # 0-100 scale
    date_added: Optional[datetime]
    last_reviewed: Optional[datetime]
    review_count: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

### SaveWordRequest
```python
class SaveWordRequest(BaseModel):
    finnish_word: str
    user_id: str
```

### UpdateWordStatusRequest
```python
class UpdateWordStatusRequest(BaseModel):
    status: WordStatus
    proficiency: Optional[int]
```

---

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# OpenAI API Key (optional, for AI-powered definitions)
OPENAI_API_KEY=sk-...

# Database URL (for PostgreSQL production)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/learning_finnish

# Feature Flag for AI Practice
ENABLE_AI_PRACTICE=true
```

### Settings

The AI service is configured in `app/config.py`:
```python
openai_api_key: Optional[str] = None
```

If `openai_api_key` is not set, the service will automatically use mock data for demonstrations and testing.

---

## AI Service

The `AIService` class in `app/services/ai_service.py` provides:

1. **Word Definition Generation**: Creates clear, concise definitions suitable for language learners
2. **Grammatical Form Analysis**: Generates nominative, genitive, and partitive cases
3. **Example Sentence Generation**: Creates contextual example sentences
4. **Automatic Fallback**: Uses realistic mock data if OpenAI API is unavailable

### Mock Data

When the OpenAI API is not available, the service returns pre-defined mock data for:
- **kissa** (cat)
- **kirja** (book)
- **vesi** (water)
- **koulu** (school)
- And 10+ other common Finnish words

---

## Usage Examples

### Search for a Word
```bash
curl -X POST "http://localhost:8001/api/words/search?finnish_word=kissa" \
  -H "Content-Type: application/json"
```

### Save a Word to Your Wordbook
```bash
curl -X POST "http://localhost:8001/api/words/save" \
  -H "Content-Type: application/json" \
  -d '{
    "finnish_word": "kissa",
    "user_id": "user-123"
  }'
```

### Get Your Saved Words
```bash
curl -X GET "http://localhost:8001/api/words/user-words/user-123?status=learning&limit=50" \
  -H "Content-Type: application/json"
```

### Update Word Status
```bash
curl -X PUT "http://localhost:8001/api/words/word-123/status/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "learning",
    "proficiency": 65
  }'
```

### Get AI Definition
```bash
curl -X GET "http://localhost:8001/api/words/word-123/ai-definition" \
  -H "Content-Type: application/json"
```

---

## Error Handling

All endpoints follow consistent error handling:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- `200`: Successful GET or POST request
- `201`: Resource created
- `204`: Resource deleted
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Server error

---

## Performance Considerations

1. **Database Indexes**: The `finnish_word` field is indexed for fast lookups
2. **Query Optimization**: Uses `selectinload` to efficiently load related word data
3. **Caching**: AI definitions are cached in the database to avoid repeated API calls
4. **Pagination**: Use `limit` and `offset` parameters for large result sets

---

## Testing

The endpoints can be tested using:
- FastAPI's built-in Swagger UI: `http://localhost:8001/docs`
- FastAPI's ReDoc: `http://localhost:8001/redoc`
- cURL commands
- Postman or similar API clients

---

## Integration with Frontend

Example React integration:

```typescript
// Search for a word
const searchWord = async (finnishWord: string) => {
  const response = await fetch(`/api/words/search?finnish_word=${finnishWord}`, {
    method: 'POST',
  });
  return await response.json();
};

// Save word to wordbook
const saveWord = async (finnishWord: string, userId: string) => {
  const response = await fetch('/api/words/save', {
    method: 'POST',
    body: JSON.stringify({
      finnish_word: finnishWord,
      user_id: userId,
    }),
  });
  return await response.json();
};

// Get user's words
const getUserWords = async (userId: string, status?: string) => {
  const url = `/api/words/user-words/${userId}${status ? `?status=${status}` : ''}`;
  const response = await fetch(url);
  return await response.json();
};

// Update word status
const updateWordStatus = async (
  wordId: string,
  userId: string,
  status: 'recent' | 'learning' | 'mastered',
  proficiency?: number
) => {
  const response = await fetch(`/api/words/${wordId}/status/${userId}`, {
    method: 'PUT',
    body: JSON.stringify({
      status,
      proficiency,
    }),
  });
  return await response.json();
};
```

---

## Files Changed

1. **app/models_db.py**: Added `Word` and `UserWord` database models with `WordStatusEnum`
2. **app/models/__init__.py**: Added Pydantic schemas for word API
3. **app/services/ai_service.py**: Created AI service for definitions and examples
4. **app/routers/words.py**: Created word lookup and management endpoints
5. **app/main.py**: Registered words router
6. **requirements.txt**: Added `openai==1.3.0` dependency
7. **backend/WORDS_API_DOCUMENTATION.md**: This documentation file

---

## Future Enhancements

- Word frequency tracking and suggestions
- Spaced repetition algorithm for optimal review timing
- Audio pronunciation support
- Word etymology and related words
- Custom word lists and collections
- Interactive flashcard system
- Progress analytics and statistics
