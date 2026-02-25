#!/bin/bash
# Learning Finnish — Run all tests
#
# e2e (TypeScript Playwright) — browser/UI tests
# API (Python)               — FastAPI endpoint tests
#
# Usage:
#   ./scripts/test.sh                                     # all tests, localhost defaults
#   API_BASE_URL=http://dobbybrain:8001 ./scripts/test.sh # API tests against homelab

set -e
cd "$(dirname "$0")/.."

export API_BASE_URL="${API_BASE_URL:-http://localhost:8001}"

echo "=== e2e tests (TypeScript Playwright) ==="
npx playwright test e2e/ --reporter=line

echo ""
echo "=== API tests (Python) — $API_BASE_URL ==="
cd tests/playwright
python3 test_smoke.py
python3 test_api_words.py
python3 test_api_exercise.py

echo ""
echo "All tests passed."
