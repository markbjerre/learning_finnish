# Tailscale Setup for Finnish DB

**Status:** ✅ Complete (Feb 18, 2026)

Tailscale creates a private network between your homelab and VPS — works through CGNAT, no port forwarding needed.

---

## Step 1: Create Tailscale Account (if needed)

1. Go to https://tailscale.com
2. Sign up (free) with Google, GitHub, or Microsoft
3. You'll use this to authenticate both machines

---

## Step 2: Install Tailscale on Homelab

SSH in and run:

```bash
ssh markbj@192.168.0.252
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

A URL will appear — open it in your browser and approve the homelab device.

---

## Step 3: Authenticate VPS

The VPS already has Tailscale installed. You need to authenticate it.

**Option A — Auth key (recommended for servers):**

1. Go to https://login.tailscale.com/admin/settings/keys
2. Click "Generate auth key"
3. Check "Reusable" and "Ephemeral" (optional)
4. Copy the key (starts with `tskey-auth-`)

Then run (I can do this if you provide the key):

```bash
tailscale up --authkey=YOUR_AUTH_KEY
```

**Option B — Login URL:**

Run on VPS: `tailscale up` — a URL will appear. Open it and approve.

---

## Step 4: Get Tailscale IPs

After both are connected:

```bash
# On homelab
tailscale ip -4

# On VPS  
tailscale ip -4
```

Note the homelab's Tailscale IP (e.g. 100.x.x.x).

---

## Step 5: Expose finnish-db on Tailscale

The DB currently binds to 127.0.0.1:5433. We need to allow Tailscale access.

Update the homelab docker-compose to bind to 0.0.0.0:5433 (Tailscale network is private).

---

## Step 6: Test Connection

From VPS:

```bash
PGPASSWORD=$FINNISH_DB_PASSWORD psql -h dobbybrain -p 5433 -U learning_finnish -d learning_finnish -c "SELECT version();"
```

## Completed Setup

- **Homelab hostname:** dobbybrain (100.83.229.69)
- **VPS hostname:** srv1070976 (100.77.253.18)
- **Connection string:** `postgresql+asyncpg://learning_finnish:${FINNISH_DB_PASSWORD}@dobbybrain:5433/learning_finnish` (from backend/.env)
