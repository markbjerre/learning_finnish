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

## AUTOMATED DEPLOYMENT: GITHUB WEBHOOKS

**Status:** ✅ ACTIVE (Nov 9, 2025)

### Overview
This repository is configured with automatic deployment via GitHub webhooks. When you push to the `main` branch, the system automatically:
1. Pulls latest code from GitHub
2. Rebuilds the Docker container
3. Restarts the service
4. Verifies health checks

**No manual deployment needed!**

### Webhook Configuration
- **Endpoint:** `https://ai-vaerksted.cloud/webhook`
- **Secret:** Stored in VPS `/root/.env` as `WEBHOOK_SECRET`
- **Events:** Push events on `main` branch only
- **Status:** ✅ Verified working (tested Nov 9, 2025)

### How It Works

When you push to GitHub:
1. GitHub sends a POST request to the webhook endpoint with HMAC-SHA256 signature
2. Webhook service validates the signature using the shared secret
3. Service identifies the repository name from the payload
4. Executes the corresponding update script:
   - **learning_finnish** → `/opt/webhook-scripts/update-finnish.sh`
5. Script runs asynchronously in the webhook container
6. Container restarts automatically when rebuild completes

### Update Script Details

**File:** `/opt/webhook-scripts/update-finnish.sh`

```bash
#!/bin/bash
set -e

REPO_DIR="/opt/ai-vaerksted/Finnish-Learning"
CONTAINER_NAME="ai-vaerksted-finnish"

echo "[$(date)] Finnish webhook triggered - pulling latest changes..."

cd "$REPO_DIR"
git fetch origin main
git reset --hard origin/main

echo "[$(date)] Finnish code updated. Rebuilding container..."

cd /root
docker compose up -d --no-deps --build $CONTAINER_NAME

echo "[$(date)] Finnish deployment complete!"
```

### Testing the Webhook

**Manual Test:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d '{"repository":{"name":"learning_finnish"},"ref":"refs/heads/main"}' \
  https://ai-vaerksted.cloud/webhook
```

Response: `200 OK` with body "Deployment started"

**Automatic Test:**
Push a commit to the `main` branch. Monitor progress:
```bash
ssh root@72.61.179.126
docker logs ai-vaerksted-webhook -f
docker ps | grep finnish
```

### Infrastructure Requirements

For webhooks to work, the following must be in place:

1. **Network/Firewall:**
   - VPS port 443 (HTTPS) open to GitHub IP ranges
   - GitHub can reach `https://ai-vaerksted.cloud/webhook`

2. **DNS:**
   - Domain `ai-vaerksted.cloud` must resolve correctly
   - SSL certificate must be valid (Let's Encrypt via Traefik)

3. **Docker Setup:**
   - Docker socket mounted at `/var/run/docker.sock` (read-write)
   - `/opt/ai-vaerksted/` mounted in webhook container (read-write for git operations)
   - `/opt/webhook-scripts/` mounted read-only for update scripts

4. **Git Configuration:**
   - SSH key configured for GitHub cloning
   - `git` command available in webhook container

5. **Secrets:**
   - `WEBHOOK_SECRET` environment variable set in docker-compose
   - Must match GitHub webhook secret exactly

### Troubleshooting

**Webhook returns 404:**
- Check Traefik routing: `docker logs root-traefik-1 | grep webhook`
- Verify webhook labels in docker-compose.yml

**Script fails with "git: command not found":**
- Git not installed in webhook container
- Rebuild webhook: `docker compose build --no-cache webhook`

**Script fails with "No such file or directory":**
- Repository not cloned to `/opt/ai-vaerksted/`
- Check: `ls -la /opt/ai-vaerksted/Finnish-Learning/`

**Container doesn't restart:**
- Docker socket not mounted in webhook container
- Check: `docker exec ai-vaerksted-webhook ls -l /var/run/docker.sock`

### Related Documentation
- Main Infrastructure: See `/root/docker-compose.yml`
- Webhook Server Code: See DobbyBrain folder `webhook/` directory
- All Update Scripts: `/opt/webhook-scripts/update-*.sh`

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

**Last Updated:** November 9, 2025 (Auto-Deploy via GitHub Webhooks Activated)
