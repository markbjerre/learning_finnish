# Learning Finnish

AI-powered Finnish language learning application.

## Stack
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Flask + Gunicorn
- **Deployment:** Docker + Traefik

## Development

```bash
# Install dependencies
npm install

# Run dev server (frontend at :8080, backend at :8000)
npm run dev

# Build for production
npm run build
```

## Deployment

The app is deployed to `https://ai-vaerksted.cloud/finnish`

### How Routing Works
- Traefik strips `/finnish` prefix before routing to the Flask app
- Vite base is `/` (assets build to `/assets/*`)
- React Router basename is `/` (routes relative to /)
- Flask serves SPA with fallback to index.html for all routes

Result: Browser URL `/finnish/*` → Traefik strips → Flask gets `/` → React handles routing
