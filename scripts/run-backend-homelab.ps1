# Run Learning Finnish backend connected to homelab PostgreSQL via Tailscale
# Requires: Tailscale running, FINNISH_DB_PASSWORD in backend/.env
# Do NOT set USE_SQLITE - config uses homelab when FINNISH_DB_PASSWORD is set
$backendDir = Resolve-Path (Join-Path $PSScriptRoot "..\backend")
Set-Location $backendDir
& .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
