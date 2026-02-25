"""
Shared configuration for Learning Finnish API tests.

Set API_BASE_URL to target different environments:
  http://localhost:8001     - FastAPI local (default)
  http://dobbybrain:8001   - Homelab via Tailscale
  https://ai-vaerksted.cloud/finnish/api  - Production
"""
import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8001")
API_BASE = API_BASE_URL.rstrip("/")
