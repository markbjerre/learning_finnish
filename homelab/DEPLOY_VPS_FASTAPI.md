# Deploy Finnish Learning FastAPI on VPS

**Prerequisites:** Homelab finnish-db running, Tailscale on both VPS and homelab.

---

## Quick Deploy (Finnish in main compose)

### 1. SSH to VPS

```bash
ssh root@72.61.179.126
```

### 2. Ensure repo exists and is up to date

```bash
cd /opt/ai-vaerksted
if [ ! -d "Finnish-Learning" ]; then
  git clone git@github.com:markbjerre/learning_finnish.git Finnish-Learning
else
  cd Finnish-Learning && git pull origin main && cd ..
fi
```

### 3. Add database URL to .env

Edit the main compose `.env` (e.g. `/root/.env` or wherever your compose reads it):

```bash
# Add or update (password from learning_finnish/backend/.env FINNISH_DB_PASSWORD):
FINNISH_DATABASE_URL=postgresql+asyncpg://learning_finnish:${FINNISH_DB_PASSWORD}@dobbybrain:5433/learning_finnish
```

> **Note:** Use `dobbybrain` (Tailscale hostname) or the homelab Tailscale IP if hostname resolution fails.

### 4. Update DobbyBrain compose and deploy

If the main compose is at `/root/docker-compose.yml`, ensure it has the updated `ai-vaerksted-finnish` service (from DobbyBrain repo). Then:

```bash
cd /root  # or wherever the main compose lives
docker compose build ai-vaerksted-finnish --no-cache
docker compose up -d ai-vaerksted-finnish
```

### 5. Verify

```bash
curl -s https://ai-vaerksted.cloud/finnish/api/health/simple
# Expected: {"status":"ok","timestamp":"..."}

curl -s https://ai-vaerksted.cloud/finnish/ | head -20
# Expected: HTML with Learning Finnish
```

---

## Standalone Deploy (docker-compose.prod.yml)

Use when running Finnish separately from the main ai-vaerksted stack.

### 1. Clone and configure

```bash
ssh root@72.61.179.126
cd /opt/ai-vaerksted
git clone git@github.com:markbjerre/learning_finnish.git Finnish-Learning
cd Finnish-Learning
```

### 2. Create .env

```bash
# Create .env with DATABASE_URL (get password from backend/.env FINNISH_DB_PASSWORD)
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://learning_finnish:YOUR_FINNISH_DB_PASSWORD@dobbybrain:5433/learning_finnish
OPENAI_API_KEY=
EOF
```

### 3. Deploy

```bash
# If Traefik runs in another compose, use that project's network:
# docker network ls  # find e.g. root_default
# Edit docker-compose.prod.yml: change traefik-network to root_default (or your network)

docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### 4. Verify

```bash
curl -s https://ai-vaerksted.cloud/finnish/api/health/simple
```

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| 502 Bad Gateway | Container running? `docker ps \| grep finnish` |
| DB connection refused | Tailscale up on both? `tailscale status` |
| 404 on /finnish | Traefik labels correct? PathPrefix `/finnish` |
| Frontend blank | Build with VITE_BASE_PATH=/finnish/ |

### Test DB from VPS

```bash
PGPASSWORD=$FINNISH_DB_PASSWORD psql -h dobbybrain -p 5433 -U learning_finnish -d learning_finnish -c "SELECT 1"
```

---

## Reference

- **Homelab DB:** `192.168.0.252` (dobbybrain on Tailscale)
- **Connection:** `postgresql+asyncpg://learning_finnish:PASSWORD@dobbybrain:5433/learning_finnish`
- **Live URL:** https://ai-vaerksted.cloud/finnish
