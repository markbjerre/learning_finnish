#!/bin/bash
# Run with: sudo bash setup_finnish_tunnel.sh
# Run from homelab (192.168.0.252)

set -e

# Create user if not exists
id finnish-tunnel &>/dev/null || useradd -r -s /usr/sbin/nologin -m -d /home/finnish-tunnel finnish-tunnel

# Create .ssh and authorized_keys
mkdir -p /home/finnish-tunnel/.ssh
cat > /home/finnish-tunnel/.ssh/authorized_keys << 'EOF'
command="echo Access restricted",no-agent-forwarding,no-X11-forwarding,permitopen="127.0.0.1:5433" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO1j0ogSYtjLqIblztZUOV9vhO9r5l1GLzy2KdYczuYT vps-finnish-tunnel
EOF

chmod 700 /home/finnish-tunnel/.ssh
chmod 600 /home/finnish-tunnel/.ssh/authorized_keys
chown -R finnish-tunnel:finnish-tunnel /home/finnish-tunnel

echo "finnish-tunnel user configured successfully."
