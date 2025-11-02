# Deployment Instructions - Finnish Learning App

## Overview

This project consists of two parts:
1. **Frontend (React/Vite)** - Deployed via Lovable
2. **Backend (Flask/Python)** - Deployed on VPS at `ai-vaerksted.cloud/finnish`

## Backend Deployment (VPS)

### 1. Setup Repository

Create a repository on your VPS with the backend files:

```bash
# On VPS
cd /opt/ai-vaerksted
git clone <your-finnish-learning-repo>
cd Finnish-Learning/backend
```

### 2. Add to Docker Compose

Edit `/root/docker-compose.yml` and add:

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

### 3. Deploy Backend

```bash
cd /opt/ai-vaerksted/Finnish-Learning/backend
docker build -t ai-vaerksted-finnish:latest .
cd /root
docker-compose up -d ai-vaerksted-finnish
```

### 4. Verify Backend

```bash
curl https://ai-vaerksted.cloud/finnish/health
curl https://ai-vaerksted.cloud/finnish/api/word/talo
```

Expected response from `/health`:
```json
{"status": "ok"}
```

## Frontend Deployment (Lovable)

### 1. Set Environment Variable

In your Lovable project, create a `.env` file (or set in production settings):

```env
VITE_API_URL=https://ai-vaerksted.cloud/finnish
```

### 2. Deploy via Lovable

1. Click "Publish" button in Lovable
2. App will be deployed with your custom domain

## API Endpoints

The Flask backend provides:

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/word/<word>?source_lang=fi&target_lang=da` - Get word details
- `POST /api/translate` - Translate text

## Local Development

### Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
python app.py
```

Backend runs on `http://localhost:8000`

### Frontend (React)

```bash
npm install
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

Frontend runs on `http://localhost:8080`

## Architecture

```
┌─────────────┐      HTTPS      ┌──────────────┐
│   Browser   │ ───────────────> │   Lovable    │
│             │                  │   (React)    │
└─────────────┘                  └──────────────┘
                                        │
                                        │ API calls
                                        ▼
                              ┌──────────────────┐
                              │   VPS Server     │
                              │  Traefik Proxy   │
                              └──────────────────┘
                                        │
                              /finnish/ │
                                        ▼
                              ┌──────────────────┐
                              │  Flask Backend   │
                              │   (Docker)       │
                              │   Port 8000      │
                              └──────────────────┘
```

## Environment Variables

### Backend (.env)
```
FLASK_ENV=production
OPENAI_API_KEY=your_openai_api_key
```

### Frontend (.env)
```
VITE_API_URL=https://ai-vaerksted.cloud/finnish
```

## Troubleshooting

### Backend not responding
```bash
# Check logs
docker logs ai-vaerksted-finnish

# Restart container
docker-compose restart ai-vaerksted-finnish
```

### CORS errors
- Ensure Flask-CORS is installed and configured in `app.py`
- Check that CORS headers are properly set

### 404 errors
- Verify Traefik labels in docker-compose.yml
- Check path stripping middleware is active
- Ensure Flask routes don't include `/finnish` prefix

### API connection errors in frontend
- Verify `VITE_API_URL` is set correctly
- Check browser console for exact error messages
- Test backend health endpoint directly

## Next Steps

1. Implement OpenAI integration in Flask backend
2. Add authentication to protect API endpoints
3. Add database for storing user word lists
4. Implement caching for frequently requested words
