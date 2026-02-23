# Finnish DB Setup: Migration + Secure VPS Connection

## Overview

What we're doing:
1. Migrate the `finnish-db` PostgreSQL container data to `/mnt/seagate_8TB/`
2. Set up SSH key auth from VPS → homelab
3. Create a persistent SSH tunnel so VPS (OpenClaw + FastAPI) can reach the DB
4. Test the full connection

```
Your PC (Windows)                VPS (72.61.179.126)
     |                               |
     | SSH                           | SSH tunnel (autossh)
     v                               v
Homelab (192.168.0.252)  <--- encrypted tunnel ---> port 5432
     |
     v
finnish-db (PostgreSQL on /mnt/seagate_8TB/)
```

---

## Phase 1: Migrate PostgreSQL Data to External Drive

### 1.1 SSH into your homelab

From your Windows PC:
```bash
ssh markbj@192.168.0.252
```

### 1.2 Check current state

```bash
# See if finnish-db is running
docker ps -a | grep finnish

# Check current volume
docker volume inspect finnish_db_data 2>/dev/null || docker volume inspect docker_finnish_db_data 2>/dev/null

# Check if there's any data to preserve
docker exec finnish-db psql -U learning_finnish -d learning_finnish -c '\dt' 2>/dev/null
```

If the container doesn't exist yet or has no important data, skip to **1.4**.

### 1.3 Backup existing data (if any)

```bash
# Create backup directory on external drive
sudo mkdir -p /mnt/seagate_8TB/finnish/backups

# Dump the database
docker exec finnish-db pg_dump -U learning_finnish -d learning_finnish > /mnt/seagate_8TB/finnish/backups/finnish_db_backup_$(date +%Y%m%d).sql

# Verify the backup
head -20 /mnt/seagate_8TB/finnish/backups/finnish_db_backup_*.sql
```

### 1.4 Create directory structure on external drive

```bash
# Create the postgres data directory
sudo mkdir -p /mnt/seagate_8TB/finnish/postgres_data

# Set ownership (postgres in the container runs as UID 999 or 70 depending on image)
# We'll let the container handle permissions on first start
sudo chmod 700 /mnt/seagate_8TB/finnish/postgres_data
```

### 1.5 Stop and remove old container (if running)

```bash
# Stop the old container
docker stop finnish-db 2>/dev/null
docker rm finnish-db 2>/dev/null

# Don't remove the old volume yet — keep it as backup until we verify
```

### 1.6 Create new docker-compose for the Finnish DB

Create the compose file on the homelab:

```bash
mkdir -p /home/markbj/homelab/apps/finnish-db
cat > /home/markbj/homelab/apps/finnish-db/docker-compose.yml << 'EOF'
version: '3.8'

services:
  finnish-db:
    image: postgres:15-alpine
    container_name: finnish-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: learning_finnish
      POSTGRES_USER: learning_finnish
      POSTGRES_PASSWORD: ${FINNISH_DB_PASSWORD}
    ports:
      - "127.0.0.1:5433:5432"  # Only localhost! Port 5433 to avoid conflicts
    volumes:
      - /mnt/seagate_8TB/finnish/postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U learning_finnish"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - finnish-network

networks:
  finnish-network:
    driver: bridge
EOF
```

### 1.7 Create .env file with a strong password

```bash
# Generate a strong password
FINNISH_PW=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
echo "FINNISH_DB_PASSWORD=${FINNISH_PW}" > /home/markbj/homelab/apps/finnish-db/.env
chmod 600 /home/markbj/homelab/apps/finnish-db/.env

# IMPORTANT: Note this password — you'll need it on the VPS too
echo "===== SAVE THIS PASSWORD ====="
cat /home/markbj/homelab/apps/finnish-db/.env
echo "==============================="
```

### 1.8 Start the new container

```bash
cd /home/markbj/homelab/apps/finnish-db
docker compose up -d

# Wait for healthy
sleep 5
docker ps | grep finnish-db

# Verify it's running on the external drive
ls -la /mnt/seagate_8TB/finnish/postgres_data/
```

### 1.9 Restore backup (if you had existing data)

```bash
# Find your backup
ls /mnt/seagate_8TB/finnish/backups/

# Restore it
cat /mnt/seagate_8TB/finnish/backups/finnish_db_backup_*.sql | docker exec -i finnish-db psql -U learning_finnish -d learning_finnish

# Verify
docker exec finnish-db psql -U learning_finnish -d learning_finnish -c '\dt'
```

### 1.10 Verify the database works

```bash
# Connect and check
docker exec -it finnish-db psql -U learning_finnish -d learning_finnish -c "SELECT version();"

# Check it's listening on 5433 (localhost only)
ss -tlnp | grep 5433
```

✅ **Checkpoint**: PostgreSQL is running on `/mnt/seagate_8TB/`, accessible on `127.0.0.1:5433`.

---

## Phase 2: Set Up SSH Key Auth (VPS → Homelab)

The VPS needs to SSH into the homelab to create the tunnel. We'll use key-based auth (no passwords).

### 2.1 On the VPS: Generate SSH key

SSH into your VPS first:
```bash
ssh root@72.61.179.126
```

Then generate a dedicated key:
```bash
# Create a key specifically for the tunnel
ssh-keygen -t ed25519 -C "vps-finnish-tunnel" -f ~/.ssh/finnish_tunnel_key -N ""

# View the public key (you'll need this)
cat ~/.ssh/finnish_tunnel_key.pub
```

**Copy the output** — it looks like: `ssh-ed25519 AAAA...long-string... vps-finnish-tunnel`

### 2.2 On the homelab: Create a restricted tunnel user

SSH into homelab from your Windows PC:
```bash
ssh markbj@192.168.0.252
```

Create a dedicated user that can ONLY do port forwarding:
```bash
# Create user with no password login, no shell
sudo useradd -r -s /usr/sbin/nologin -m -d /home/finnish-tunnel finnish-tunnel

# Create .ssh directory
sudo mkdir -p /home/finnish-tunnel/.ssh
sudo chmod 700 /home/finnish-tunnel/.ssh

# Add the VPS public key (paste what you copied in 2.1)
# Replace the key below with YOUR actual key from step 2.1
sudo bash -c 'cat > /home/finnish-tunnel/.ssh/authorized_keys << EOF
command="echo Access restricted",no-agent-forwarding,no-X11-forwarding,permitopen="127.0.0.1:5433" ssh-ed25519 PASTE_YOUR_KEY_HERE vps-finnish-tunnel
EOF'

sudo chmod 600 /home/finnish-tunnel/.ssh/authorized_keys
sudo chown -R finnish-tunnel:finnish-tunnel /home/finnish-tunnel/.ssh
```

The `authorized_keys` line restricts this key to **only** port forwarding to `127.0.0.1:5433`. Even if the key is compromised, it can't run commands or access anything else.

### 2.3 Allow the tunnel user to SSH with port forwarding

```bash
# Edit SSH config to allow this user
sudo bash -c 'cat >> /etc/ssh/sshd_config << EOF

# Finnish DB tunnel user — port forwarding only
Match User finnish-tunnel
    AllowTcpForwarding local
    PermitOpen 127.0.0.1:5433
    X11Forwarding no
    AllowAgentForwarding no
    ForceCommand echo "Port forwarding only"
    PermitTTY no
EOF'

# Test SSH config is valid
sudo sshd -t

# If no errors, restart SSH
sudo systemctl restart sshd
```

### 2.4 Configure your router/firewall

Your homelab is behind your home network. The VPS needs to reach it. You have two options:

**Option A: Port forward on your router (simplest)**
1. Log into your router admin panel
2. Forward an external port (e.g. `2222`) to `192.168.0.252:22`
3. Note your home public IP (check: `curl ifconfig.me` from homelab)

**Option B: Dynamic DNS (if your home IP changes)**
1. Set up DuckDNS, No-IP, or similar
2. Point a hostname like `markbj-home.duckdns.org` to your home IP
3. Install the DDNS update client on your homelab

**Which to use**: If your ISP gives you a static IP, Option A is fine. If dynamic, use Option B.

### 2.5 Test SSH from VPS → homelab

From the VPS:
```bash
# Replace YOUR_HOME_IP with your home public IP (or DDNS hostname)
# Replace 2222 with whatever port you forwarded
ssh -i ~/.ssh/finnish_tunnel_key -p 2222 finnish-tunnel@YOUR_HOME_IP

# Expected output: "Port forwarding only" then disconnects
# This is CORRECT — the user can't get a shell
```

If this works, the VPS can reach your homelab.

✅ **Checkpoint**: VPS can SSH to homelab with restricted key.

---

## Phase 3: Create Persistent SSH Tunnel

### 3.1 On the VPS: Install autossh

`autossh` automatically reconnects if the tunnel drops.

```bash
apt update && apt install -y autossh
```

### 3.2 Test the tunnel manually first

```bash
# This forwards VPS localhost:5433 → homelab localhost:5433 (where PostgreSQL listens)
ssh -i ~/.ssh/finnish_tunnel_key \
    -p 2222 \
    -N -L 127.0.0.1:5433:127.0.0.1:5433 \
    finnish-tunnel@YOUR_HOME_IP

# In another VPS terminal, test the connection:
psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "SELECT 1;"
# Enter the FINNISH_DB_PASSWORD when prompted

# If you see "1" — the tunnel works!
# Ctrl+C to stop the manual tunnel
```

### 3.3 Create a systemd service for the tunnel

This makes the tunnel start on boot and auto-restart:

```bash
cat > /etc/systemd/system/finnish-db-tunnel.service << 'EOF'
[Unit]
Description=SSH tunnel to homelab Finnish PostgreSQL
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/autossh -M 0 \
    -o "ServerAliveInterval 30" \
    -o "ServerAliveCountMax 3" \
    -o "ExitOnForwardFailure yes" \
    -o "StrictHostKeyChecking accept-new" \
    -i /root/.ssh/finnish_tunnel_key \
    -p 2222 \
    -N -L 127.0.0.1:5433:127.0.0.1:5433 \
    finnish-tunnel@YOUR_HOME_IP
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Replace YOUR_HOME_IP in the file
# nano /etc/systemd/system/finnish-db-tunnel.service

# Enable and start
systemctl daemon-reload
systemctl enable finnish-db-tunnel
systemctl start finnish-db-tunnel

# Check status
systemctl status finnish-db-tunnel
```

### 3.4 Verify the persistent tunnel

```bash
# Check the tunnel is running
ss -tlnp | grep 5433

# Test the database connection
psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "SELECT version();"

# Check logs if something is wrong
journalctl -u finnish-db-tunnel -f
```

✅ **Checkpoint**: Persistent tunnel running. VPS can reach homelab PostgreSQL at `127.0.0.1:5433`.

---

## Phase 4: Verify Full Connection

### 4.1 Test from VPS with psql

```bash
# Install psql client on VPS if not present
apt install -y postgresql-client

# Connect through the tunnel
psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish
```

Once connected, run:
```sql
-- Should return PostgreSQL version
SELECT version();

-- Create a test table to verify writes work
CREATE TABLE tunnel_test (id SERIAL, msg TEXT);
INSERT INTO tunnel_test (msg) VALUES ('tunnel works!');
SELECT * FROM tunnel_test;
DROP TABLE tunnel_test;
```

### 4.2 Connection string for FastAPI

When you later set up the FastAPI backend on the VPS, use this connection string:

```
DATABASE_URL=postgresql+asyncpg://learning_finnish:YOUR_PASSWORD@127.0.0.1:5433/learning_finnish
```

This connects through the SSH tunnel to your homelab PostgreSQL.

### 4.3 Test from OpenClaw (if using HTTP tools)

The FastAPI will run on the VPS and talk to `127.0.0.1:5433` — OpenClaw talks to FastAPI, not directly to the DB. So the chain is:

```
OpenClaw → FastAPI (localhost:8000) → SSH tunnel (localhost:5433) → Homelab PostgreSQL
```

---

## Troubleshooting

### Tunnel won't connect
```bash
# Test SSH manually with verbose output
ssh -v -i ~/.ssh/finnish_tunnel_key -p 2222 finnish-tunnel@YOUR_HOME_IP

# Common issues:
# - Router port forward not set up
# - Home IP changed (check from homelab: curl ifconfig.me)
# - SSH service not running on homelab
# - Key not in authorized_keys
```

### Tunnel connects but DB is unreachable
```bash
# On homelab: verify PostgreSQL is listening on 5433
ssh markbj@192.168.0.252
ss -tlnp | grep 5433
docker ps | grep finnish-db

# Check container is binding to 127.0.0.1:5433
docker port finnish-db
```

### Tunnel keeps dropping
```bash
# Check autossh logs
journalctl -u finnish-db-tunnel --since "1 hour ago"

# Common causes:
# - Home internet instability
# - Router restarting
# - ISP changing your public IP → set up DDNS
```

### Can't install psql on VPS
```bash
# Alternative: test with Python
python3 -c "
import subprocess
result = subprocess.run(['pg_isready', '-h', '127.0.0.1', '-p', '5433'], capture_output=True, text=True)
print(result.stdout)
"

# Or just proceed to Phase 1 of the main project and let FastAPI test the connection
```

---

## Security Summary

| Layer | Protection |
|-------|-----------|
| SSH key | Ed25519, dedicated key for tunnel only |
| Tunnel user | No shell, no agent forwarding, restricted to port 5433 |
| PostgreSQL | Binds to `127.0.0.1` only — not exposed to internet |
| Router | Only port 2222 forwarded, only to homelab SSH |
| DB password | Random 24-char password, stored in `.env` |
| Tunnel | Encrypted end-to-end via SSH |

**What's NOT exposed to the internet:**
- PostgreSQL port (only localhost)
- Any homelab services
- Shell access via tunnel key

---

## Next Steps

Once this is all working:
1. → **Create the Finnish DB schema** (tables from the project plan v2) — ✅ Done
2. → **Deploy FastAPI on VPS** connecting to `dobbybrain:5433` via Tailscale — ✅ Ready
3. → **Set up OpenClaw skill** pointing at FastAPI

---

## Update (Feb 18, 2026): Tailscale Instead of SSH Tunnel

Port forwarding failed due to CGNAT (SIM router). **Tailscale** was used instead:

- Homelab and VPS both run Tailscale
- VPS connects to `dobbybrain:5433` over the Tailscale private network
- No port forwarding required
- See `homelab/TAILSCALE_SETUP.md` and `UPDATE_SUMMARY.md`