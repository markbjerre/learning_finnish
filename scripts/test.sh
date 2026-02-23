#!/bin/bash
# Learning Finnish — verify build (no automated test suite)
# Usage: ./scripts/test.sh

set -e
cd "$(dirname "$0")/.."
npm run build
