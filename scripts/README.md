# Learning Finnish Scripts

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
