# Deployment Instructions - Finnish Learning App

## Project Overview

**Project Type:** Full-stack web application for learning Finnish  
**Repository:** learning_finnish (markbjerre/learning_finnish)  
**Current Branch:** main  

**Architecture:**
- **Frontend:** React + Vite + TypeScript (shadcn-ui, Tailwind CSS)
- **Backend:** Flask (Python) + OpenAI API
- **Deployment:** Frontend on Lovable, Backend on VPS with Docker + Traefik

---

## Deployment Infrastructure

### Production Environment

**VPS Details:**
- **Domain:** ai-vaerksted.cloud
- **Backend Path:** /opt/ai-vaerksted/Finnish-Learning
- **Backend URL:** https://ai-vaerksted.cloud/finnish
- **Reverse Proxy:** Traefik (for SSL and routing)
- **Container Name:** ai-vaerksted-finnish
- **Internal Port:** 8000 (mapped via Traefik)

**Frontend:**
- **Platform:** Lovable (https://lovable.dev)
- **Project URL:** https://lovable.dev/projects/1f40692c-cca4-4916-b08d-d5818e2b22fe
- **Deployment:** Automatic via Lovable's publish feature

---

## File Structure

```
learning_finnish/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Docker image configuration
│   ├── cache.py                 # Caching system for performance
│   ├── prompts/                 # AI prompt templates
│   │   ├── __init__.py
│   │   └── word_lookup.py       # Prompt builders
│   ├── cache/                   # Cache storage (auto-created)
│   ├── test_api.py              # API testing script
│   ├── test_speed.py            # Performance testing
│   ├── test_local_api.py        # Local API testing
│   └── .env.example             # Environment template
├── src/                         # Frontend React code
│   ├── components/              # UI components
│   ├── pages/                   # Page components
│   ├── services/
│   │   └── api.ts              # API service (connects to backend)
│   └── ...
├── .env                         # Environment variables
├── package.json                 # Node dependencies
├── vite.config.ts              # Vite configuration
├── README.md                    # Project documentation
└── DEPLOYMENT.md                # Deployment guide

```

---

## Backend Files for VPS Deployment

### Critical Files to Upload:

1. **backend/app.py** - Main Flask application
2. **backend/requirements.txt** - Python dependencies
3. **backend/Dockerfile** - Docker build configuration
4. **backend/cache.py** - Caching system
5. **backend/prompts/** - All prompt files
   - `prompts/__init__.py`
   - `prompts/word_lookup.py`
6. **backend/.env** - Environment variables (with OPENAI_API_KEY)

### Backend Dependencies (requirements.txt):

```
flask==2.3.3
werkzeug==2.3.7
gunicorn==21.2.0
flask-cors==4.0.0
openai>=1.50.0
python-dotenv==1.0.0
requests==2.31.0
```

---

## Environment Configuration

### Backend Environment Variables (.env)

**Location:** `/opt/ai-vaerksted/Finnish-Learning/backend/.env`

```env
FLASK_ENV=production
OPENAI_API_KEY=your_openai_api_key_here
```

**Security Note:** Keep OPENAI_API_KEY only in backend .env on VPS

### Frontend Environment Variables (.env)

**For Local Development:**
```env
VITE_API_URL=http://localhost:5003
OPENAI_API_KEY=your_key_here
```

**For Production (Lovable):**
```env
VITE_API_URL=https://ai-vaerksted.cloud/finnish
```

---

## Docker Configuration

### Dockerfile

**Location:** `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

### Docker Compose Entry

**Location:** `/root/docker-compose.yml` on VPS

```yaml
ai-vaerksted-finnish:
  build: /opt/ai-vaerksted/Finnish-Learning/backend
  container_name: ai-vaerksted-finnish
  networks:
    - default
  environment:
    - FLASK_ENV=production
    - OPENAI_API_KEY=${OPENAI_API_KEY}
  labels:
    - traefik.enable=true
    - 'traefik.http.routers.finnish.rule=Host(`ai-vaerksted.cloud`) && PathPrefix(`/finnish`)'
    - traefik.http.routers.finnish.entrypoints=websecure
    - traefik.http.routers.finnish.tls.certresolver=mytlschallenge
    - 'traefik.http.middlewares.finnish-strip.stripprefix.prefixes=/finnish'
    - traefik.http.routers.finnish.middlewares=finnish-strip
    - traefik.http.services.finnish.loadbalancer.server.port=8000
```

**Key Configuration Details:**
- **PathPrefix:** `/finnish` - All requests to https://ai-vaerksted.cloud/finnish/* route to this service
- **Strip Prefix:** Removes `/finnish` from URL before passing to Flask app
- **Port:** Internal port 8000 (Flask with Gunicorn)
- **SSL:** Automatic via Traefik with Let's Encrypt

---

## Deployment Steps

### 1. Initial Setup (One-Time)

**On VPS:**

```bash
# Navigate to project directory
cd /opt/ai-vaerksted

# Clone repository (if not exists)
git clone <repository-url> Finnish-Learning

# Navigate to backend
cd Finnish-Learning/backend

# Create .env file
nano .env
# Add: OPENAI_API_KEY=your_key_here
# Add: FLASK_ENV=production
```

### 2. Building and Deploying Backend

**On VPS:**

```bash
# Navigate to backend directory
cd /opt/ai-vaerksted/Finnish-Learning/backend

# Build Docker image
docker build -t ai-vaerksted-finnish:latest .

# Navigate to docker-compose directory
cd /root

# Start/restart the service
docker-compose up -d ai-vaerksted-finnish
```

### 3. Verification

```bash
# Check container status
docker ps | grep finnish

# Check logs
docker logs ai-vaerksted-finnish

# Test health endpoint
curl https://ai-vaerksted.cloud/finnish/health

# Test word lookup
curl https://ai-vaerksted.cloud/finnish/api/word/talo
```

### 4. Frontend Deployment

**On Lovable Platform:**

1. Update `.env` in Lovable project:
   ```env
   VITE_API_URL=https://ai-vaerksted.cloud/finnish
   ```

2. Click "Publish" button in Lovable interface

3. Frontend automatically deploys to Lovable's hosting

---

## Update Procedure

### When Code Changes Are Made:

**For Backend Updates:**

```bash
# On VPS
cd /opt/ai-vaerksted/Finnish-Learning

# Pull latest changes
git pull origin main

# Rebuild Docker image
cd backend
docker build -t ai-vaerksted-finnish:latest .

# Restart container
cd /root
docker-compose up -d ai-vaerksted-finnish

# Verify deployment
docker logs -f ai-vaerksted-finnish
curl https://ai-vaerksted.cloud/finnish/health
```

**For Frontend Updates:**

Changes pushed to GitHub are automatically detected by Lovable and can be deployed via the Lovable interface.

---

## API Endpoints

### Health Check
```
GET https://ai-vaerksted.cloud/finnish/health
Response: {"status": "ok"}
```

### Word Lookup
```
GET https://ai-vaerksted.cloud/finnish/api/word/<word>?source_lang=fi&target_lang=da

Response:
{
  "word": "talo",
  "translation": "hus",
  "pronunciation": "ˈtɑlo",
  "partOfSpeech": "substantiv",
  "forms": {...},
  "example": "...",
  "wordHints": [...],
  "memoryAid": "...",
  "category": "substantiv",
  "_timing": {...}
}
```

### Translation
```
POST https://ai-vaerksted.cloud/finnish/api/translate
Body: {"text": "...", "source_lang": "fi", "target_lang": "da"}

Response:
{
  "original": "...",
  "translation": "...",
  "source_lang": "fi",
  "target_lang": "da",
  "_timing": {...}
}
```

### Cache Stats
```
GET https://ai-vaerksted.cloud/finnish/api/cache/stats
Response: {"memory_cache_size": 10, "file_cache_size": 10, "cache_dir": "cache"}
```

### Clear Cache
```
POST https://ai-vaerksted.cloud/finnish/api/cache/clear
Body: {"word": "talo"} (optional - omit to clear all)
```

---

## File Upload Strategy for Orchestration

### Priority 1: Core Backend Files
These must be uploaded first:

1. `backend/requirements.txt` - Install dependencies
2. `backend/Dockerfile` - Build container
3. `backend/.env` - Configuration (NEVER commit to git)
4. `backend/app.py` - Main application
5. `backend/cache.py` - Caching system

### Priority 2: Supporting Modules
Upload after core files:

6. `backend/prompts/__init__.py`
7. `backend/prompts/word_lookup.py`

### Priority 3: Optional Files
These improve functionality but aren't critical:

8. `backend/test_api.py` - Testing
9. `backend/test_speed.py` - Performance testing
10. `backend/README.md` - Documentation

### Deployment Sequence:

```bash
# 1. Upload all files to /opt/ai-vaerksted/Finnish-Learning/backend/
# 2. Ensure .env exists with OPENAI_API_KEY
# 3. Build Docker image
# 4. Update docker-compose.yml if needed
# 5. Deploy container
# 6. Verify endpoints
```

---

## Performance Features

### Caching System

**Implementation:** In-memory + file-based cache  
**Location:** `backend/cache/` directory (auto-created)  
**TTL:** 24 hours (configurable)  

**Performance:**
- **First Request (Cold):** 1-3 seconds (OpenAI API call)
- **Cached Request (Hot):** < 50ms (cache lookup)
- **Speedup:** 20-60x faster for cached words

**Cache Management:**
- Automatic expiry after 24 hours
- Manual clearing via API endpoint
- Persistent across server restarts (file-based)

---

## Troubleshooting

### Container Not Starting
```bash
# Check logs
docker logs ai-vaerksted-finnish

# Common issues:
# - Missing OPENAI_API_KEY in .env
# - Port 8000 already in use
# - Syntax error in app.py
```

### 404 Errors
```bash
# Verify Traefik routing
docker logs traefik

# Check path stripping is configured
# Ensure Flask routes don't include /finnish prefix
```

### Slow Response Times
```bash
# Check if caching is working
curl https://ai-vaerksted.cloud/finnish/api/cache/stats

# First requests are slow (OpenAI API)
# Subsequent requests should be fast (cached)
```

### CORS Errors
```bash
# Verify flask-cors is installed
# Check CORS configuration in app.py
# Ensure frontend URL is allowed
```

---

## Security Considerations

1. **API Key Protection:**
   - OPENAI_API_KEY must only exist in backend/.env on VPS
   - Never commit .env to git
   - Use environment variables in Docker

2. **HTTPS:**
   - All traffic via Traefik with Let's Encrypt SSL
   - Automatic certificate renewal

3. **Rate Limiting:**
   - Consider adding rate limiting to prevent API abuse
   - OpenAI API has built-in rate limits

---

## Monitoring

### Check Service Health
```bash
# Container status
docker ps | grep finnish

# Resource usage
docker stats ai-vaerksted-finnish

# Recent logs
docker logs --tail=100 ai-vaerksted-finnish

# Follow logs in real-time
docker logs -f ai-vaerksted-finnish
```

### Performance Metrics
```bash
# Cache statistics
curl https://ai-vaerksted.cloud/finnish/api/cache/stats

# Test response time
time curl https://ai-vaerksted.cloud/finnish/api/word/talo
```

---

## Rollback Procedure

If deployment fails:

```bash
# Stop new container
docker-compose stop ai-vaerksted-finnish

# Remove container
docker-compose rm -f ai-vaerksted-finnish

# Rebuild from previous version
cd /opt/ai-vaerksted/Finnish-Learning
git checkout <previous-commit>
cd backend
docker build -t ai-vaerksted-finnish:latest .

# Restart
cd /root
docker-compose up -d ai-vaerksted-finnish
```

---

## Contact & Support

**Repository:** markbjerre/learning_finnish  
**Lovable Project:** https://lovable.dev/projects/1f40692c-cca4-4916-b08d-d5818e2b22fe  
**VPS Domain:** ai-vaerksted.cloud

---

## Summary for Orchestration LLM

**Key Points:**
1. Backend files must be uploaded to `/opt/ai-vaerksted/Finnish-Learning/backend/`
2. Ensure `.env` file exists with `OPENAI_API_KEY` before building
3. Build Docker image: `docker build -t ai-vaerksted-finnish:latest .`
4. Deploy via: `docker-compose up -d ai-vaerksted-finnish` from `/root`
5. Verify: `curl https://ai-vaerksted.cloud/finnish/health`
6. Frontend deploys separately via Lovable platform

**Critical Files to Upload:**
- app.py, cache.py, requirements.txt, Dockerfile, .env
- prompts/__init__.py, prompts/word_lookup.py

**Docker Configuration:**
- Container name: ai-vaerksted-finnish
- Internal port: 8000
- Public URL: https://ai-vaerksted.cloud/finnish
- Traefik handles routing and SSL

**Environment:**
- FLASK_ENV=production
- OPENAI_API_KEY=<secret>
