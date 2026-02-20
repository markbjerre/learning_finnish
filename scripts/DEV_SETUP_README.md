# Development Scripts

This directory contains helper scripts for setting up and running your development environment.

## Quick Start

### macOS/Linux

```bash
# Full setup (all dependencies + environments)
bash scripts/setup-dev-env.sh

# With Docker
bash scripts/setup-dev-env.sh --docker

# Just Learning Finnish
bash scripts/dev-finnish.sh
```

### Windows (PowerShell)

```powershell
# Full setup (all dependencies + environments)
powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1

# With Docker
powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1 -Docker
```

---

## Scripts

### `setup-dev-env.sh` (macOS/Linux)

Complete development environment setup for all projects.

**Features:**
- ✅ Checks system dependencies
- ✅ Installs Node.js dependencies (npm)
- ✅ Installs Python dependencies (pip)
- ✅ Creates virtual environments
- ✅ Sets up `.env` files
- ✅ Starts Docker containers (optional)

**Usage:**
```bash
bash scripts/setup-dev-env.sh              # Local development
bash scripts/setup-dev-env.sh --docker     # Docker development
bash scripts/setup-dev-env.sh --help       # Show help
```

**What it does:**
1. Verifies Node.js, Python 3.11+, and Git are installed
2. Installs all frontend dependencies (React, Vite, Tailwind)
3. Creates Python virtual environments for all backends
4. Installs all Python dependencies
5. Creates basic `.env` files for backends
6. Provides instructions for starting dev servers

**Time:** ~5-10 minutes (depending on internet speed)

---

### `setup-dev-env.ps1` (Windows)

Windows PowerShell version of the setup script.

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1 -Docker
powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1 -Help
```

**Features:** (same as bash version)
- Checks dependencies
- Installs Node.js packages
- Sets up Python environments
- Configures environment variables

---

### `dev-finnish.sh` (macOS/Linux)

Quick script to start Learning Finnish frontend + backend.

**Usage:**
```bash
bash scripts/dev-finnish.sh
```

**Starts:**
- Frontend (Vite): http://localhost:5173
- Backend (Flask): http://localhost:8000

**Stops:** Press Ctrl+C

---

## Project-Specific Setup

### Learning Finnish

```bash
# Frontend only
cd learning_finnish && npm run dev

# Backend only  
cd learning_finnish/backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
flask run
```

### Finance Dashboard

```bash
cd "Finance dashboard"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

### Wedding

```bash
cd Wedding/markella-boho-celebration
npm install
npm run dev
```

### Housing Market Search

```bash
cd "Danish Housing Market Search"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

---

## Docker Development

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Stop all services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f finnish-backend

# Rebuild containers
docker-compose -f docker-compose.dev.yml up --build
```

---

## Testing

### Run All Tests

```bash
npx playwright test --ui
```

### Run Specific Test File

```bash
npx playwright test e2e/learning-finnish.spec.ts
```

### Debug Mode

```bash
npx playwright test --debug
```

### Generate Test Code

```bash
npx playwright codegen http://localhost:5173
```

---

## Environment Variables

### Learning Finnish Backend

```env
FLASK_ENV=development
FLASK_DEBUG=1
```

### Finance Dashboard

```env
FLASK_ENV=development
FLASK_DEBUG=1
OPENAI_API_KEY=sk_...          # Get from openai.com
NEWSAPI_KEY=...                # Get from newsapi.org
SUPABASE_URL=...
SUPABASE_KEY=...
```

### Wedding

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=...
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5173
lsof -i :5173

# Kill it
kill -9 <PID>
```

### Python Virtual Environment Not Activating

```bash
# Make sure you're in the right directory
cd learning_finnish/backend

# Create new venv
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### npm Dependency Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Docker Containers Won't Start

```bash
# Check if ports are in use
docker ps

# Remove old containers
docker-compose -f docker-compose.dev.yml down

# Rebuild and start
docker-compose -f docker-compose.dev.yml up --build
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Learning Finnish Frontend | 5173 | http://localhost:5173 |
| Learning Finnish Backend | 8000 | http://localhost:8000 |
| Finance Dashboard | 5002 | http://localhost:5002 |
| Website Front Page | 8002 | http://localhost:8002 |
| Housing Market | 8003 | http://localhost:8003 |
| Wedding | 5174 | http://localhost:5174 |

---

## Developer Documentation

For detailed development guides, see the `CLAUDE_DEV.md` files in each project:

- `learning_finnish/CLAUDE_DEV.md` - Learning Finnish development guide
- `Finance dashboard/CLAUDE_DEV.md` - Finance Dashboard development guide
- `Danish Housing Market Search/CLAUDE_DEV.md` - Housing Market development guide
- `Website Front Page/CLAUDE_DEV.md` - Front Page development guide
- `Wedding/markella-boho-celebration/CLAUDE_DEV.md` - Wedding site development guide

---

## Getting Help

Use Claude Code to:
- Ask about setup issues
- Get debugging help
- Request feature guidance
- Review code changes

Check the project-specific `CLAUDE_DEV.md` files for detailed information on each project's architecture and development workflow.
