#!/bin/bash
# Run on homelab: curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up
# Or run this script with: sudo bash install_tailscale_homelab.sh

set -e
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
echo "Done. Run 'tailscale ip -4' to get your Tailscale IP."
