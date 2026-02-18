# Finnish DB — Phase 2, 3 & 4: SSH Tunnel Setup

**For:** Cursor Agent  
**Date:** February 18, 2026  
**Prerequisite:** Phase 1 Complete (see UPDATE_SUMMARY.md)  
**Goal:** Establish a persistent, secure SSH tunnel from the VPS to the homelab PostgreSQL database.

---

## Context

Phase 1 is done. PostgreSQL is running on the homelab:

| Item | Value |
|------|-------|
| **Homelab IP** | `192.168.0.252` |
| **Homelab user** | `markbj` |
| **Homelab SSH** | port 22 |
| **Home public IP** | Static (user will provide when prompted) |
| **VPS IP** | `72.61.179.126` |
| **VPS user** | `root` |
| **DB container** | `finnish-db` |
| **DB port** | `127.0.0.1:5433` on homelab |
| **DB name** | `learning_finnish` |
| **DB user** | `learning_finnish` |
| **DB password** | `aZxa3LcafGOFgYkZyrURIwiO` |
| **Compose path** | `/home/markbj/homelab/apps/finnish-db/` |

The VPS cannot currently reach the homelab. We need to:
1. Create SSH key on VPS
2. Create restricted tunnel user on homelab
3. User sets up router port forward (manual step)
4. Create persistent autossh tunnel on VPS
5. Verify DB is reachable from VPS

---

## IMPORTANT: Execution Rules

- This involves **two remote servers**. You will need to SSH into each.
- **VPS access:** `ssh root@72.61.179.126`
- **Homelab access:** `ssh markbj@192.168.0.252`
- You CANNOT SSH from VPS → homelab yet. That's what we're setting up.
- Execute steps in order. Do not skip ahead.
- After Phase 2 step 4 (router port forward), **STOP and ask the user** to do this manually — you cannot access their router.
- After any SSH command, verify the output before proceeding.
- The user's home IP is static. You will need to **ask the user** for their home public IP once.

---

## Phase 2: SSH Key Auth (VPS → Homelab)

### Step 2.1 — Generate SSH key on VPS

SSH into the VPS and run:

```bash
ssh root@72.61.179.126
```

Then:

```bash
# Generate a dedicated Ed25519 key for the tunnel
ssh-keygen -t ed25519 -C "vps-finnish-tunnel" -f /root/.ssh/finnish_tunnel_key -N ""

# Output the public key — we need this for the homelab
cat /root/.ssh/finnish_tunnel_key.pub
```

**Save the public key output.** You need it for Step 2.2.

### Step 2.2 — Create restricted tunnel user on homelab

SSH into the homelab (from local machine, NOT from VPS):

```bash
ssh markbj@192.168.0.252
```

Then create a user that can ONLY do port forwarding:

```bash
# Create user with no login shell
sudo useradd -r -s /usr/sbin/nologin -m -d /home/finnish-tunnel finnish-tunnel

# Create .ssh directory
sudo mkdir -p /home/finnish-tunnel/.ssh
sudo chmod 700 /home/finnish-tunnel/.ssh
```

Now add the VPS public key. **Replace `PASTE_VPS_PUBLIC_KEY_HERE`** with the actual key from Step 2.1:

```bash
sudo bash -c 'cat > /home/finnish-tunnel/.ssh/authorized_keys << EOF
command="echo Access restricted",no-agent-forwarding,no-X11-forwarding,permitopen="127.0.0.1:5433" PASTE_VPS_PUBLIC_KEY_HERE
EOF'

sudo chmod 600 /home/finnish-tunnel/.ssh/authorized_keys
sudo chown -R finnish-tunnel:finnish-tunnel /home/finnish-tunnel/.ssh
```

### Step 2.3 — Configure SSH daemon on homelab

Still on the homelab:

```bash
# Check if a finnish-tunnel Match block already exists
grep -n "finnish-tunnel" /etc/ssh/sshd_config
```

If it does NOT exist, add it:

```bash
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
```

Validate and restart SSH:

```bash
# CRITICAL: Validate config before restarting. If this fails, DO NOT restart sshd.
sudo sshd -t
```

If `sshd -t` returns no output (success):

```bash
sudo systemctl restart sshd
```

If `sshd -t` returns errors: **STOP. Show the error to the user. Do not restart sshd.**

### Step 2.4 — Router port forward (MANUAL USER STEP)

**⚠️ STOP HERE AND ASK THE USER TO DO THIS MANUALLY:**

Tell the user:
> I need you to set up a port forward on your home router:
>
> - **External port:** `2222`
> - **Internal IP:** `192.168.0.252`
> - **Internal port:** `22`
> - **Protocol:** TCP
>
> Also, please tell me your **home public IP address**. You can check it by running `curl ifconfig.me` on the homelab, or by visiting https://ifconfig.me in a browser.
>
> Let me know when the port forward is active and share your public IP.

**Wait for the user to confirm and provide their public IP before continuing.**

### Step 2.5 — Test SSH from VPS → homelab

Once the user provides their home public IP (referred to as `HOME_PUBLIC_IP` below), SSH into the VPS:

```bash
ssh root@72.61.179.126
```

Test the connection:

```bash
ssh -i /root/.ssh/finnish_tunnel_key -p 2222 -o ConnectTimeout=10 finnish-tunnel@HOME_PUBLIC_IP
```

**Expected output:** `Port forwarding only` then the connection closes. This is correct — the user has no shell.

**If it fails:**
- `Connection refused` → Router port forward not set up or wrong port
- `Connection timed out` → Wrong public IP or firewall blocking
- `Permission denied` → Key not in authorized_keys correctly
- Show the error to the user and troubleshoot.

**If it succeeds:** Proceed to Phase 3.

---

## Phase 3: Persistent SSH Tunnel

### Step 3.1 — Install autossh on VPS

On the VPS:

```bash
apt update && apt install -y autossh
```

### Step 3.2 — Test tunnel manually

```bash
# Start a manual tunnel (foreground, for testing)
ssh -i /root/.ssh/finnish_tunnel_key \
    -p 2222 \
    -N -L 127.0.0.1:5433:127.0.0.1:5433 \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    finnish-tunnel@HOME_PUBLIC_IP &

# Wait for it to establish
sleep 3

# Test the database connection through the tunnel
# Install psql if not present
which psql || apt install -y postgresql-client

PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "SELECT version();"
```

**Expected:** PostgreSQL version string. If this works, the tunnel is functional.

```bash
# Kill the background tunnel
kill %1 2>/dev/null
```

**If the psql test fails:**
- `Connection refused on port 5433` → Tunnel didn't establish. Check SSH output.
- `Password authentication failed` → Wrong password. Check UPDATE_SUMMARY.md.
- `Could not connect to server` → Tunnel not running. Re-run the ssh command without `&` to see errors.

### Step 3.3 — Create systemd service

Create the service file on the VPS. **Replace `HOME_PUBLIC_IP`** with the actual IP:

```bash
cat > /etc/systemd/system/finnish-db-tunnel.service << 'SERVICEEOF'
[Unit]
Description=SSH tunnel to homelab Finnish PostgreSQL
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=AUTOSSH_GATETIME=0
ExecStart=/usr/bin/autossh -M 0 \
    -o "ServerAliveInterval 30" \
    -o "ServerAliveCountMax 3" \
    -o "ExitOnForwardFailure yes" \
    -o "StrictHostKeyChecking accept-new" \
    -o "ConnectTimeout 10" \
    -i /root/.ssh/finnish_tunnel_key \
    -p 2222 \
    -N -L 127.0.0.1:5433:127.0.0.1:5433 \
    finnish-tunnel@HOME_PUBLIC_IP
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF
```

**IMPORTANT:** After creating the file, replace the placeholder:

```bash
# Replace HOME_PUBLIC_IP with the actual IP provided by the user
sed -i 's/HOME_PUBLIC_IP/ACTUAL_IP_HERE/' /etc/systemd/system/finnish-db-tunnel.service

# Verify the file looks correct
cat /etc/systemd/system/finnish-db-tunnel.service
```

Enable and start:

```bash
systemctl daemon-reload
systemctl enable finnish-db-tunnel
systemctl start finnish-db-tunnel

# Wait for connection
sleep 5

# Check status
systemctl status finnish-db-tunnel
```

**Expected:** Active (running), no errors.

### Step 3.4 — Verify persistent tunnel

```bash
# Check port is listening
ss -tlnp | grep 5433

# Test DB connection
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "SELECT version();"
```

**If the service fails to start:**
```bash
# Check logs
journalctl -u finnish-db-tunnel --no-pager -n 30
```

Show errors to the user.

---

## Phase 4: Verify Full Connection & Create Schema

### Step 4.1 — End-to-end database test

On the VPS, connect through the tunnel and run a full test:

```bash
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish << 'SQL'
-- Test basic connectivity
SELECT version();
SELECT current_database(), current_user, inet_server_addr(), inet_server_port();

-- Test write capability
CREATE TABLE IF NOT EXISTS _tunnel_test (id SERIAL, msg TEXT, ts TIMESTAMPTZ DEFAULT NOW());
INSERT INTO _tunnel_test (msg) VALUES ('VPS tunnel connection verified');
SELECT * FROM _tunnel_test;
DROP TABLE _tunnel_test;
SQL
```

**Expected:** All queries succeed. The tunnel is production-ready.

### Step 4.2 — Create the Finnish learning schema

Still connected to the DB from the VPS:

```bash
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish << 'SQL'

-- Core vocabulary
CREATE TABLE IF NOT EXISTS words (
    id                SERIAL PRIMARY KEY,
    finnish           TEXT NOT NULL,
    danish            TEXT,
    english           TEXT,
    word_type         TEXT NOT NULL,
    grammatical_notes TEXT,
    tags              TEXT[],
    priority          FLOAT DEFAULT 1.0,
    times_served      INT DEFAULT 0,
    total_score       FLOAT DEFAULT 0.0,
    last_score        FLOAT,
    last_served       TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Finnish inflections (cases)
CREATE TABLE IF NOT EXISTS inflections (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    case_name     TEXT NOT NULL,
    singular      TEXT,
    plural        TEXT,
    notes         TEXT,
    UNIQUE(word_id, case_name)
);

-- Verb conjugations
CREATE TABLE IF NOT EXISTS verb_forms (
    id            SERIAL PRIMARY KEY,
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    form_name     TEXT NOT NULL,
    form_value    TEXT NOT NULL,
    tense         TEXT,
    notes         TEXT,
    UNIQUE(word_id, form_name, tense)
);

-- Grammatical concepts
CREATE TABLE IF NOT EXISTS concepts (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    description   TEXT,
    examples      JSONB,
    tags          TEXT[],
    priority      FLOAT DEFAULT 1.0,
    times_served  INT DEFAULT 0,
    total_score   FLOAT DEFAULT 0.0,
    last_score    FLOAT,
    last_served   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Word to concept links
CREATE TABLE IF NOT EXISTS word_concepts (
    word_id       INT REFERENCES words(id) ON DELETE CASCADE,
    concept_id    INT REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (word_id, concept_id)
);

-- Exercise history
CREATE TABLE IF NOT EXISTS exercise_log (
    id              SERIAL PRIMARY KEY,
    exercise_type   TEXT NOT NULL,
    level_used      INT,
    words_used      INT[],
    concepts_used   INT[],
    prompt_sent     TEXT,
    user_response   TEXT,
    ai_feedback     TEXT,
    word_scores     JSONB,
    concept_scores  JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- System settings
CREATE TABLE IF NOT EXISTS settings (
    key           TEXT PRIMARY KEY,
    value         JSONB NOT NULL
);

-- Initialize default settings (skip if already exist)
INSERT INTO settings (key, value) VALUES ('level', '15') ON CONFLICT (key) DO NOTHING;
INSERT INTO settings (key, value) VALUES ('exercise_word_count', '5') ON CONFLICT (key) DO NOTHING;
INSERT INTO settings (key, value) VALUES ('random_ratio', '0.25') ON CONFLICT (key) DO NOTHING;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_words_priority ON words(priority DESC);
CREATE INDEX IF NOT EXISTS idx_words_finnish ON words(finnish);
CREATE INDEX IF NOT EXISTS idx_words_word_type ON words(word_type);
CREATE INDEX IF NOT EXISTS idx_inflections_word_id ON inflections(word_id);
CREATE INDEX IF NOT EXISTS idx_verb_forms_word_id ON verb_forms(word_id);
CREATE INDEX IF NOT EXISTS idx_concepts_priority ON concepts(priority DESC);
CREATE INDEX IF NOT EXISTS idx_exercise_log_created ON exercise_log(created_at DESC);

-- Verify
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

SQL
```

**Expected output:** Table list showing: `concepts`, `exercise_log`, `inflections`, `settings`, `verb_forms`, `word_concepts`, `words`.

### Step 4.3 — Record the connection string

The FastAPI backend on the VPS should use:

```
DATABASE_URL=postgresql+asyncpg://learning_finnish:aZxa3LcafGOFgYkZyrURIwiO@127.0.0.1:5433/learning_finnish
```

---

## Verification Checklist

After completing all phases, verify:

```bash
# On VPS:

# 1. Tunnel service is running
systemctl is-active finnish-db-tunnel
# Expected: active

# 2. Port 5433 is listening
ss -tlnp | grep 5433
# Expected: LISTEN on 127.0.0.1:5433

# 3. Can connect to DB
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "SELECT COUNT(*) FROM words;"
# Expected: count = 0 (empty table, ready for data)

# 4. Schema is correct
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -c "\dt"
# Expected: 7 tables listed

# 5. Tunnel auto-restarts
systemctl is-enabled finnish-db-tunnel
# Expected: enabled
```

---

## Update UPDATE_SUMMARY.md

After all phases are complete, update `/learning_finnish/UPDATE_SUMMARY.md`:

- Change status to: `Phase 1-4 Complete`
- Add Phase 2 completion date
- Add Phase 3 completion date
- Add Phase 4 completion date
- Add the home public IP used (for reference)
- Add note that schema has been created with 7 tables
- Add the VPS connection string

---

## Troubleshooting Reference

| Problem | Check | Fix |
|---------|-------|-----|
| SSH timeout from VPS | Router port forward | User must configure 2222 → 192.168.0.252:22 |
| SSH permission denied | authorized_keys on homelab | Verify key matches, permissions 600 |
| sshd won't restart | Config syntax | Run `sudo sshd -t`, fix errors |
| Tunnel connects but no DB | Finnish-db container running? | `ssh markbj@192.168.0.252 "docker ps \| grep finnish"` |
| psql auth failure | Password mismatch | Check `.env` at `/home/markbj/homelab/apps/finnish-db/.env` |
| Tunnel drops frequently | Network instability | autossh handles reconnection; check `journalctl -u finnish-db-tunnel` |
| Service won't start | Bad systemd file | `journalctl -u finnish-db-tunnel --no-pager -n 50` |