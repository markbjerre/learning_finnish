# Finnish DB Setup — Update Summary

**Date:** February 18, 2026  
**Status:** Phase 1–4 Complete | Tailscale connected (SSH tunnel bypassed due to CGNAT)

---

## Overview

Migration of the Learning Finnish PostgreSQL database to the homelab external drive, with VPS access via Tailscale (bypasses CGNAT/SIM router).

```
Your PC (Windows)                VPS (72.61.179.126)
     |                               |
     | SSH                           | Tailscale VPN
     v                               v
Homelab (192.168.0.252)  <--- dobbybrain:5433 ---> FastAPI
     |                               |
     v                               v
finnish-db (PostgreSQL on /mnt/seagate_8TB/)
```

---

## Phase 1: Migrate PostgreSQL to External Drive — COMPLETE

### Completed Steps

| Step | Action | Status |
|------|--------|--------|
| 1.1 | SSH to homelab | Done |
| 1.2 | Check current state (no existing finnish-db) | Done |
| 1.3 | Backup existing data | Skipped (no data) |
| 1.4 | Create `/mnt/seagate_8TB/finnish/postgres_data` | Done |
| 1.5 | Stop/remove old container | Skipped (none existed) |
| 1.6 | Copy docker-compose.yml to homelab | Done |
| 1.7 | Create .env with strong password | Done |
| 1.8 | `docker compose up -d` | Done |
| 1.9 | Restore backup | Skipped |
| 1.10 | Verify with `SELECT version();` | Done |

### Deployment Details

| Item | Value |
|------|-------|
| **Host** | 192.168.0.252 (homelab) |
| **Container** | finnish-db |
| **Image** | postgres:15-alpine |
| **Data path** | `/mnt/seagate_8TB/finnish/postgres_data` |
| **Listen** | `0.0.0.0:5433` (Tailscale network) |
| **Database** | learning_finnish |
| **User** | learning_finnish |
| **Compose path** | `/home/markbj/homelab/apps/finnish-db/` |

### Credentials

| Variable | Value |
|----------|-------|
| **FINNISH_DB_PASSWORD** | `aZxa3LcafGOFgYkZyrURIwiO` |

> **Important:** Store this password securely. Required for Phase 4 (VPS FastAPI connection).

### Verification

```bash
# Container status
docker ps | grep finnish-db
# Up, healthy

# Database test
docker exec finnish-db psql -U learning_finnish -d learning_finnish -c "SELECT version();"
# PostgreSQL 15.16 on x86_64-pc-linux-musl

# Port binding
ss -tlnp | grep 5433
# 127.0.0.1:5433
```

---

## Sudoers Configuration

Added passwordless sudo for mkdir/chmod to enable automated homelab setup via SSH:

**File:** `/etc/sudoers.d/markbj-finnish-setup`

```
markbj ALL=(ALL) NOPASSWD: /usr/bin/mkdir, /usr/bin/chmod
```

**Note:** `apt update`/`apt upgrade` still require interactive sudo (password).

---

## Phase 2 & 3: SSH Tunnel — BYPASSED (Tailscale)

Port forwarding failed due to CGNAT (SIM router). Replaced with **Tailscale**:

- **VPS:** Tailscale installed, authenticated (srv1070976)
- **Homelab:** Tailscale installed, authenticated (dobbybrain)
- **Connection:** VPS connects to `dobbybrain:5433` over Tailscale private network

SSH tunnel setup (finnish-tunnel user, autossh) preserved in `homelab/PHASE2_3_4_RUNBOOK.md` for reference if port forwarding becomes available.

---

## Phase 4: VPS FastAPI Connection — Ready to Deploy

### Connection String for FastAPI on VPS

```
DATABASE_URL=postgresql+asyncpg://learning_finnish:aZxa3LcafGOFgYkZyrURIwiO@dobbybrain:5433/learning_finnish
```

For DobbyBrain compose, use env var: `FINNISH_DATABASE_URL` (same value).

### Deployment

See **`homelab/DEPLOY_VPS_FASTAPI.md`** for step-by-step VPS deployment.

Summary:
1. Add `FINNISH_DATABASE_URL` to VPS `.env`
2. Build and start `ai-vaerksted-finnish` from main compose
3. Verify: `curl https://ai-vaerksted.cloud/finnish/api/health/simple`

---

## Files Created/Modified

| File | Location | Purpose |
|------|----------|---------|
| `homelab/docker-compose.yml` | learning_finnish/homelab/ | Homelab PostgreSQL compose |
| `homelab/.env.example` | learning_finnish/homelab/ | Password template |
| `homelab/DEPLOY_PHASE1.md` | learning_finnish/homelab/ | Phase 1 runbook |
| `homelab/setup_env.sh` | learning_finnish/homelab/ | Password generation script |
| `homelab/setup_finnish_tunnel.sh` | learning_finnish/homelab/ | Tunnel user setup (run with sudo) |
| `homelab/authorized_keys_finnish_tunnel` | learning_finnish/homelab/ | VPS public key for tunnel |
| `homelab/PHASE2_3_4_RUNBOOK.md` | learning_finnish/homelab/ | Phase 2–4 manual runbook |
| `homelab/finnish_schema.sql` | learning_finnish/homelab/ | DB schema |
| `homelab/duckdns-update.sh` | learning_finnish/homelab/ | DuckDNS updater (cron) |
| `homelab/TAILSCALE_SETUP.md` | learning_finnish/homelab/ | Tailscale setup guide |
| `homelab/DEPLOY_VPS_FASTAPI.md` | learning_finnish/homelab/ | VPS FastAPI deployment runbook |
| `UPDATE_SUMMARY.md` | learning_finnish/ | This file |

---

## Reference

- **Full instructions:** `finnish_2_0_instructions.md`
- **Homelab quick reference:** `192.168.0.252 control/DobbyBrain_Homelab.instructions.md`
