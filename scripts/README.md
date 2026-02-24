# Learning Finnish Scripts

## test_api_words.py

Focused API tests for `/api/words` endpoints.

### Usage

```bash
# Against running backend (default: http://localhost:8001)
python scripts/test_api_words.py
# or: npm run test:api

# In-process (no server needed, uses SQLite)
python scripts/test_api_words.py --in-process
# or: npm run test:api:in-process

# Custom base URL
python scripts/test_api_words.py --base-url http://localhost:8000
```

**Note:** For `test:api` (against server), start the backend first:

```powershell
# Windows - SQLite (no PostgreSQL)
.\scripts\run-backend-local.ps1

# Or manually with SQLite
$env:DATABASE_URL=""; cd backend; python -m uvicorn app.main:app --port 8001
```

---

## test_db_and_api.py

Tests database connection and API endpoints.

### Prerequisites

```bash
cd backend && pip install -r requirements.txt
```

### Usage

```bash
# From project root - test local dev server (http://localhost:8001)
python scripts/test_db_and_api.py

# Test production
python scripts/test_db_and_api.py --base-url https://ai-vaerksted.cloud/finnish

# DB only (requires DATABASE_URL in backend/.env)
python scripts/test_db_and_api.py --db-only

# API only
python scripts/test_db_and_api.py --api-only
```

### Environment

- `FINNISH_API_URL` - Override default API base URL
- `DATABASE_URL` - For DB tests (set in backend/.env for PostgreSQL)
