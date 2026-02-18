# Learning Finnish - Development Guide for Claude Code

## Project Overview

**Type**: Full-Stack React + Python Flask Application  
**Status**: Early-stage skeleton, ready for feature development  
**Live URL**: https://ai-vaerksted.cloud/finnish  
**Repository**: Local monorepo under `/learning_finnish`

### Architecture
```
learning_finnish/
├── src/                      # React frontend (Vite)
│   ├── components/designs/   # Design variations
│   ├── pages/                # Page components
│   └── App.tsx               # Main app entry
├── backend/                  # Flask backend
│   ├── app.py                # Flask app with CORS
│   └── requirements.txt
├── public/                   # Static assets
└── Dockerfile.dev            # Development container
```

---

## Development Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Vite | Port 5173 (dev), SPA routing |
| **Backend** | Python 3.11, Flask, CORS | Port 8000, JSON API |
| **Build** | Vite, Tailwind CSS | Hot module reload (HMR) |
| **Testing** | Playwright (configured) | E2E test suite |
| **Database** | PostgreSQL (homelab) | Via Tailscale: `dobbybrain:5433` |

---

## Getting Started

### Quick Start (Docker)
```bash
# From project root
docker-compose -f docker-compose.dev.yml up finnish-frontend finnish-backend

# Frontend: http://localhost:5173
# Backend: http://localhost:8001
# API Base: http://localhost:8001
```

### Local Development (No Docker)
```bash
# Terminal 1: Frontend
cd learning_finnish
npm install
npm run dev
# http://localhost:5173

# Terminal 2: Backend
cd learning_finnish/backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
flask run
# http://localhost:8000
```

### Environment Variables

**Frontend** (`.env.local`):
```env
VITE_API_URL=http://localhost:8001
NODE_ENV=development
```

**Backend** (`.env`):
```env
FLASK_ENV=development
FLASK_DEBUG=1
# Production (VPS): connects to homelab via Tailscale
DATABASE_URL=postgresql+asyncpg://learning_finnish:PASSWORD@dobbybrain:5433/learning_finnish
```

---

## Agent Utilization Strategy

### For Feature Development
Use **fullstack-developer** agent:
```
Task: "Add vocabulary lesson module"
├─ Frontend: Create lesson component in src/components
├─ Backend: Add /api/lessons endpoint
├─ Styling: Tailwind CSS for design consistency
└─ Testing: Write Playwright E2E tests
```

**Recommended approach:**
1. Split frontend and backend into separate requests
2. Let agent handle complete file creation and imports
3. Use code-reviewer for validation
4. Test with Playwright before committing

### For UI/Design Changes
Use **fullstack-developer** with design focus:
- Modify components in `src/components/designs/`
- Update Tailwind configuration as needed
- Use existing design patterns (Dark, Minimalist, Playful)

### For Testing
Use **fullstack-developer** for Playwright tests:
- Write tests in `tests/` directory
- Test both happy path and error scenarios
- Use page fixtures for component testing

### For Performance Issues
Use **Refactoring-specialist**:
- Optimize React rendering (React.memo, useMemo)
- Minimize bundle size (code splitting)
- Improve API request efficiency

---

## Development Workflow

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/lesson-module
   ```

2. **Frontend changes** (if applicable)
   - Edit files in `src/components/` or `src/pages/`
   - Vite auto-reloads (HMR enabled)
   - Test in browser at http://localhost:5173

3. **Backend changes** (if applicable)
   - Edit files in `backend/app.py` or create modules
   - Flask auto-reloads (debug mode)
   - Test API endpoints with curl or Postman

4. **Test with Playwright**
   ```bash
   npx playwright test --ui
   ```

5. **Code review**
   - Use code-reviewer agent for validation
   - Check for security issues (XSS, CORS, etc.)

6. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add vocabulary lesson module"
   git push origin feature/lesson-module
   ```

---

## API Endpoints

### Health Check
```
GET /health
GET /api/health
Response: {"status": "ok"}
```

### Root SPA Route
```
GET /
Response: index.html (serves React app)
```

### Future Endpoints (To Be Implemented)
```
POST /api/lessons          - Create lesson
GET  /api/lessons/<id>     - Fetch lesson
PUT  /api/lessons/<id>     - Update lesson
DELETE /api/lessons/<id>   - Delete lesson
POST /api/progress         - Track user progress
```

---

## File Structure Reference

### Key Frontend Files
- `src/App.tsx` - Main app component
- `src/main.tsx` - React entry point
- `src/pages/DesignSelector.tsx` - Design selector UI
- `src/components/designs/*.tsx` - Design variations
- `vite.config.ts` - Vite bundler config
- `tailwind.config.js` - Tailwind CSS config

### Key Backend Files
- `backend/app.py` - Flask application
- `backend/requirements.txt` - Python dependencies
- `backend/.env` - Environment configuration

### Config Files
- `package.json` - Frontend dependencies
- `tsconfig.json` - TypeScript configuration
- `index.html` - HTML entry point
- `Dockerfile.dev` - Development container

---

## Testing

### Run Tests
```bash
# All tests
npx playwright test

# Watch mode (recommended for development)
npx playwright test --watch

# UI mode (best for debugging)
npx playwright test --ui

# Specific test
npx playwright test tests/lesson-creation.spec.ts
```

### Test Structure
```
tests/
├── lesson-creation.spec.ts    # Lesson CRUD operations
├── design-selector.spec.ts    # Design theme selection
└── api-integration.spec.ts    # Backend API tests
```

### Writing Tests
```typescript
// tests/example.spec.ts
import { test, expect } from '@playwright/test';

test('should load lesson page', async ({ page }) => {
  await page.goto('http://localhost:5173/lessons');
  const heading = page.getByRole('heading', { name: /learn finnish/i });
  await expect(heading).toBeVisible();
});
```

---

## MCP Servers Available

- **Docker MCP** - For container operations
- **NPM MCP** - For dependency management
- **Playwright MCP** - For browser automation
- **Git MCP** - For version control
- **GitHub MCP** - For PR/issue management
- **Filesystem MCP** - For file operations

---

## Common Tasks

### Add a new lesson type
```bash
# 1. Create component
src/components/lessons/[LessonType].tsx

# 2. Add API endpoint
backend/app.py - POST /api/lessons

# 3. Write tests
tests/[lesson-type].spec.ts

# 4. Test locally, commit, push
```

### Debug API issues
```bash
# Check backend logs
docker logs finnish-backend-dev

# Test endpoint directly
curl http://localhost:8000/api/health

# Enable Flask debug mode
FLASK_DEBUG=1 flask run
```

### Fix styling issues
```bash
# Update Tailwind classes
src/components/designs/*.tsx

# Recompile (automatic with Vite)
# Browser auto-refreshes
```

---

## Troubleshooting

### Port already in use
```bash
# Find process using port 5173
lsof -i :5173
# Kill it
kill -9 <PID>
```

### Docker container issues
```bash
# View logs
docker logs finnish-frontend-dev
docker logs finnish-backend-dev

# Rebuild containers
docker-compose -f docker-compose.dev.yml up --build

# Remove and restart
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up
```

### Module not found errors
```bash
# Reinstall dependencies
npm install

# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### API connection errors
```bash
# Check backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in frontend
echo $VITE_API_URL

# Update environment if needed
# Frontend: .env.local
# Backend: backend/.env
```

---

## Code Conventions

### TypeScript/React
- Use functional components with hooks
- Type all props and state explicitly
- Use PascalCase for component names
- Use camelCase for variables/functions
- Keep components under 300 lines

### Python/Flask
- 4-space indentation
- `snake_case` for functions/variables
- Type hints on all function signatures
- Docstrings for all functions
- Follow PEP 8 style guide

### CSS/Tailwind
- Use Tailwind utility classes
- Avoid inline CSS
- Create reusable component classes
- Mobile-first responsive design

---

## Useful Commands

```bash
# Frontend
npm run dev         # Start dev server
npm run build       # Production build
npm run preview     # Preview build locally
npm install         # Install dependencies

# Backend
flask run           # Start Flask dev server
flask shell         # Interactive Python shell
pip freeze          # List installed packages

# Docker
docker-compose -f docker-compose.dev.yml up        # Start all services
docker-compose -f docker-compose.dev.yml down      # Stop all services
docker-compose -f docker-compose.dev.yml logs -f   # View logs

# Testing
npx playwright test --ui                # Run tests with UI
npx playwright codegen localhost:5173  # Generate test code
```

---

## Next Steps

1. **Feature Development**
   - Implement lesson CRUD operations
   - Add user authentication (Supabase)
   - Create progress tracking system

2. **Database Integration**
   - Set up Supabase schema
   - Implement data persistence
   - Add caching strategies

3. **AI Features**
   - Generate lessons with LLM
   - Pronunciation feedback
   - Adaptive learning paths

4. **Deployment**
   - Configure CI/CD pipeline
   - Deploy to VPS
   - Set up monitoring

---

## Questions or Issues?

Check:
1. This guide's Troubleshooting section
2. Terminal output and logs
3. Browser console (DevTools)
4. Flask debug output

Ask Claude Code for help with:
- Feature implementation questions
- Debugging specific errors
- Architecture recommendations
- Code review and validation
