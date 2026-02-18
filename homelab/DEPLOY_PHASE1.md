# Phase 1: Deploy Finnish DB on Homelab (External Drive)

Run these commands **on your homelab** (192.168.0.252). SSH in first:

```bash
ssh markbj@192.168.0.252
```

## Step-by-step

### 1. Check current state
```bash
docker ps -a | grep finnish
docker volume inspect finnish_db_data 2>/dev/null || docker volume inspect docker_finnish_db_data 2>/dev/null
docker exec finnish-db psql -U learning_finnish -d learning_finnish -c '\dt' 2>/dev/null
```

If no container or no important data, skip to step 4.

### 2. Backup existing data (if any)
```bash
sudo mkdir -p /mnt/seagate_8TB/finnish/backups
docker exec finnish-db pg_dump -U learning_finnish -d learning_finnish > /mnt/seagate_8TB/finnish/backups/finnish_db_backup_$(date +%Y%m%d).sql
head -20 /mnt/seagate_8TB/finnish/backups/finnish_db_backup_*.sql
```

### 3. Stop and remove old container (if running)
```bash
docker stop finnish-db 2>/dev/null
docker rm finnish-db 2>/dev/null
```

### 4. Create directory structure
```bash
sudo mkdir -p /mnt/seagate_8TB/finnish/postgres_data
sudo chmod 700 /mnt/seagate_8TB/finnish/postgres_data
```

### 5. Copy deployment files to homelab

**Option A: From Windows (PowerShell), copy via SCP:**
```powershell
# Create target dir first via SSH, then copy
ssh markbj@192.168.0.252 "mkdir -p /home/markbj/homelab/apps/finnish-db"
scp "c:\Users\Mark BJ\Desktop\Code Projects\learning_finnish\homelab\docker-compose.yml" markbj@192.168.0.252:/home/markbj/homelab/apps/finnish-db/
```

**Option B: Create manually on homelab** (run after step 4):
```bash
mkdir -p /home/markbj/homelab/apps/finnish-db
nano /home/markbj/homelab/apps/finnish-db/docker-compose.yml
# Paste content from learning_finnish/homelab/docker-compose.yml
```

### 6. Create .env with strong password
```bash
cd /home/markbj/homelab/apps/finnish-db
FINNISH_PW=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
echo "FINNISH_DB_PASSWORD=${FINNISH_PW}" > .env
chmod 600 .env

echo "===== SAVE THIS PASSWORD (needed on VPS later) ====="
cat .env
echo "=================================================="
```

### 7. Start the container
```bash
docker compose up -d
sleep 5
docker ps | grep finnish-db
ls -la /mnt/seagate_8TB/finnish/postgres_data/
```

### 8. Restore backup (if you had data in step 2)
```bash
cat /mnt/seagate_8TB/finnish/backups/finnish_db_backup_*.sql | docker exec -i finnish-db psql -U learning_finnish -d learning_finnish
docker exec finnish-db psql -U learning_finnish -d learning_finnish -c '\dt'
```

### 9. Verify
```bash
docker exec -it finnish-db psql -U learning_finnish -d learning_finnish -c "SELECT version();"
ss -tlnp | grep 5433
```

**Checkpoint:** PostgreSQL running on `/mnt/seagate_8TB/`, listening on `127.0.0.1:5433`.
