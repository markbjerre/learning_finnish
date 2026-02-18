# Finnish DB — Phase 2, 3 & 4 Runbook

**Status:** Phase 2.1 complete. Steps 2.2–2.4 require manual execution (sudo + router).

---

## Completed

- **Phase 2.1:** SSH key generated on VPS at `/root/.ssh/finnish_tunnel_key`
- **Public key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO1j0ogSYtjLqIblztZUOV9vhO9r5l1GLzy2KdYczuYT vps-finnish-tunnel`

---

## Step 2.2 — Create finnish-tunnel user (run on homelab)

SSH in and run:

```bash
ssh markbj@192.168.0.252
sudo bash /tmp/setup_finnish_tunnel.sh
```

If the script is not there, run:

```bash
sudo useradd -r -s /usr/sbin/nologin -m -d /home/finnish-tunnel finnish-tunnel
sudo mkdir -p /home/finnish-tunnel/.ssh
echo 'command="echo Access restricted",no-agent-forwarding,no-X11-forwarding,permitopen="127.0.0.1:5433" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO1j0ogSYtjLqIblztZUOV9vhO9r5l1GLzy2KdYczuYT vps-finnish-tunnel' | sudo tee /home/finnish-tunnel/.ssh/authorized_keys
sudo chmod 700 /home/finnish-tunnel/.ssh
sudo chmod 600 /home/finnish-tunnel/.ssh/authorized_keys
sudo chown -R finnish-tunnel:finnish-tunnel /home/finnish-tunnel
```

---

## Step 2.3 — Configure sshd (run on homelab)

```bash
# Check if already configured
grep -n "finnish-tunnel" /etc/ssh/sshd_config
```

If no output, add:

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

# Validate
sudo sshd -t
# If no errors:
sudo systemctl restart sshd
```

---

## Step 2.4 — Router port forward (MANUAL)

Configure on your router:

- **External port:** 2222
- **Internal IP:** 192.168.0.252
- **Internal port:** 22
- **Protocol:** TCP

Get your home public IP:

```bash
curl ifconfig.me
```

Share the IP with the agent so they can continue Phase 2.5 and Phase 3.

---

## Step 2.5 — Test SSH (after port forward)

On VPS:

```bash
ssh root@72.61.179.126
ssh -i /root/.ssh/finnish_tunnel_key -p 2222 -o ConnectTimeout=10 finnish-tunnel@YOUR_HOME_IP
```

Expected: `Port forwarding only` then disconnect.

---

## Phase 3 — Persistent tunnel (after 2.5 works)

On VPS:

```bash
apt update && apt install -y autossh postgresql-client
```

Create service (replace YOUR_HOME_IP):

```bash
cat > /etc/systemd/system/finnish-db-tunnel.service << EOF
[Unit]
Description=SSH tunnel to homelab Finnish PostgreSQL
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=AUTOSSH_GATETIME=0
ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -o "ExitOnForwardFailure yes" -o "StrictHostKeyChecking accept-new" -o "ConnectTimeout 10" -i /root/.ssh/finnish_tunnel_key -p 2222 -N -L 127.0.0.1:5433:127.0.0.1:5433 finnish-tunnel@YOUR_HOME_IP
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable finnish-db-tunnel
systemctl start finnish-db-tunnel
systemctl status finnish-db-tunnel
```

---

## Phase 4 — Schema (after tunnel is running)

```bash
PGPASSWORD=aZxa3LcafGOFgYkZyrURIwiO psql -h 127.0.0.1 -p 5433 -U learning_finnish -d learning_finnish -f /path/to/schema.sql
```

See `Update_learning_finnish_2_0_continued.md` for full schema SQL.
