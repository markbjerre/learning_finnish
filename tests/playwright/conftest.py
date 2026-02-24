"""
Shared test configuration for Playwright tests.

Set TEST_BASE_URL to target different environments:
  http://localhost:8000                  - Docker local (default)
  http://localhost:5173                  - Vite dev server
  https://ai-vaerksted.cloud/finnish    - Production
"""
import os

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
API_BASE = BASE_URL.rstrip("/")
