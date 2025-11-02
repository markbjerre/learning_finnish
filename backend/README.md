# Finnish Learning API Backend

Flask backend API for the Finnish learning application.

## Quick Start

### Local Development

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the server:
```bash
python app.py
```

Server runs on `http://localhost:8000`

### Test the API

```bash
# Install requests if needed
pip install requests

# Run test suite
python test_api.py

# Or test production deployment
python test_api.py https://ai-vaerksted.cloud/finnish
```

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{"status": "ok"}
```

### Word Lookup (AI-Powered)
```bash
GET /api/word/<word>?source_lang=fi&target_lang=da
```

Example:
```bash
curl "http://localhost:8000/api/word/talo"
```

Response:
```json
{
  "word": "talo",
  "translation": "hus",
  "pronunciation": "/ˈtɑlo/",
  "partOfSpeech": "substantiv",
  "forms": {
    "nominative": "talo",
    "genitive": "talon",
    "partitive": "taloa",
    "illative": "taloon"
  },
  "example": "Minulla on suuri talo.",
  "wordHints": [
    {"word": "Minulla", "translation": "jeg har"},
    {"word": "suuri", "translation": "stor"}
  ],
  "memoryAid": "Tænk på 'talo' som et 'tal-hus' hvor man tæller husets værelser",
  "category": "substantiv"
}
```

### Translation (AI-Powered)
```bash
POST /api/translate
Content-Type: application/json

{
  "text": "Hei, kuinka voit?",
  "source_lang": "fi",
  "target_lang": "da"
}
```

Example:
```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hei, kuinka voit?","source_lang":"fi","target_lang":"da"}'
```

Response:
```json
{
  "original": "Hei, kuinka voit?",
  "translation": "Hej, hvordan har du det?",
  "source_lang": "fi",
  "target_lang": "da"
}
```

## Deployment Configuration

**Service name:** `ai-vaerksted-finnish`  
**Path:** `/opt/ai-vaerksted/Finnish-Learning`  
**URL:** `https://ai-vaerksted.cloud/finnish`  
**Port:** 8000 (internal)

## Docker Compose Entry

Add to `/root/docker-compose.yml` on VPS:

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

## Deployment Steps

### 1. Clone Repository on VPS
```bash
cd /opt/ai-vaerksted
git clone <your-repo-url> Finnish-Learning
cd Finnish-Learning
```

### 2. Set OpenAI API Key
Add to your VPS environment or `.env` file:
```bash
export OPENAI_API_KEY=your_key_here
```

### 3. Build and Deploy
```bash
cd /opt/ai-vaerksted/Finnish-Learning/backend
docker build -t ai-vaerksted-finnish:latest .
cd /root
docker-compose up -d ai-vaerksted-finnish
```

### 4. Verify Deployment
```bash
# Check health
curl https://ai-vaerksted.cloud/finnish/health

# Test word lookup
curl https://ai-vaerksted.cloud/finnish/api/word/talo

# Check logs
docker logs ai-vaerksted-finnish
```

## Updating the Deployment

```bash
cd /opt/ai-vaerksted/Finnish-Learning
git pull origin main
cd backend
docker build -t ai-vaerksted-finnish:latest .
cd /root
docker-compose up -d ai-vaerksted-finnish
```

## Troubleshooting

### Check Logs
```bash
docker logs ai-vaerksted-finnish
docker logs -f ai-vaerksted-finnish  # Follow logs
```

### Restart Service
```bash
docker-compose restart ai-vaerksted-finnish
```

### Rebuild from Scratch
```bash
docker-compose stop ai-vaerksted-finnish
docker-compose rm -f ai-vaerksted-finnish
cd /opt/ai-vaerksted/Finnish-Learning/backend
docker build --no-cache -t ai-vaerksted-finnish:latest .
cd /root
docker-compose up -d ai-vaerksted-finnish
```

### Common Issues

**OpenAI API errors:**
- Verify OPENAI_API_KEY is set correctly
- Check API quota and billing

**CORS errors:**
- flask-cors should be installed
- Check CORS configuration in app.py

**404 errors:**
- Verify Traefik path stripping is configured
- Check that routes don't include `/finnish` prefix

## Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key
- `FLASK_ENV=production` - Set production mode

## Technologies

- Python 3.11
- Flask 2.3.3
- Gunicorn 21.2.0
- OpenAI Python SDK
- Flask-CORS
