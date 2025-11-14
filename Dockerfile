# Multi-stage build: Frontend (Node) -> Backend (Python)

# Stage 1: Build React app with Vite
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN rm -rf dist && npm run build

# Stage 2: Python Flask backend serving SPA
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend from stage 1
COPY --from=frontend-build /app/dist ./static

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
