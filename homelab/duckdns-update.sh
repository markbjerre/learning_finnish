#!/bin/bash
# DuckDNS updater for markbj-homelab.duckdns.org
# Run via cron: */5 * * * * /home/markbj/duckdns-update.sh

# Load token from .duckdns.env (same dir as script, or ~/.duckdns.env)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for ENV_FILE in "${SCRIPT_DIR}/.duckdns.env" "$HOME/.duckdns.env"; do
    [ -f "$ENV_FILE" ] && source "$ENV_FILE" && break
done

if [ -z "$DUCKDNS_TOKEN" ]; then
    echo "Error: DUCKDNS_TOKEN not set. Create ${ENV_FILE} with DUCKDNS_TOKEN=your_token"
    exit 1
fi

DOMAIN="markbj-homelab"
LOG="/tmp/duckdns.log"

echo url="https://www.duckdns.org/update?domains=${DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" | curl -k -s -o "$LOG" -K -

if [ -f "$LOG" ]; then
    case "$(cat $LOG)" in
        OK) echo "$(date): DuckDNS updated OK" >> /tmp/duckdns-history.log ;;
        KO) echo "$(date): DuckDNS update failed" >> /tmp/duckdns-history.log ;;
        *) echo "$(date): DuckDNS response: $(cat $LOG)" >> /tmp/duckdns-history.log ;;
    esac
fi
