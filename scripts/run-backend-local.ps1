# Run Learning Finnish backend with SQLite (no PostgreSQL required)
# Use for local development and testing
$env:USE_SQLITE = "1"
$backendDir = Resolve-Path (Join-Path $PSScriptRoot "..\backend")
Set-Location $backendDir
& .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
