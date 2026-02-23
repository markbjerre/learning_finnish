#!/bin/bash
cd "$HOME/homelab/apps/finnish-db"
FINNISH_PW=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
echo "FINNISH_DB_PASSWORD=${FINNISH_PW}" > .env
chmod 600 .env
echo "===== SAVE THIS PASSWORD (needed on VPS for Phase 4) ====="
cat .env
echo "============================================================"
