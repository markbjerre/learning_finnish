# Finnish Learning API Backend

Flask backend API for the Finnish learning application.

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

## Deployment

```bash
cd /opt/ai-vaerksted/Finnish-Learning/backend
git pull origin main
docker build -t ai-vaerksted-finnish:latest .
cd /root
docker-compose up -d ai-vaerksted-finnish
```

## Verify

```bash
curl https://ai-vaerksted.cloud/finnish
curl https://ai-vaerksted.cloud/finnish/health
curl https://ai-vaerksted.cloud/finnish/api/word/talo
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/word/<word>?source_lang=fi&target_lang=da` - Get word details
- `POST /api/translate` - Translate text

## Environment Variables

Set in docker-compose.yml or `.env` file:

- `FLASK_ENV=production`
- `OPENAI_API_KEY=your_key_here`
