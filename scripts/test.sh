#!/bin/bash
# Learning Finnish — Run all Playwright tests
#
# Usage:
#   ./scripts/test.sh
#   TEST_BASE_URL=http://localhost:5173       ./scripts/test.sh   # Vite dev server
#   TEST_BASE_URL=https://ai-vaerksted.cloud/finnish ./scripts/test.sh   # Production

set -e
cd "$(dirname "$0")/.."

export TEST_BASE_URL="${TEST_BASE_URL:-http://localhost:8000}"
echo "Running tests against: $TEST_BASE_URL"
echo "---"

cd tests/playwright
python3 test_smoke.py
python3 test_frontend.py
python3 test_routing.py
python3 test_performance.py

echo "---"
echo "All test suites passed."
