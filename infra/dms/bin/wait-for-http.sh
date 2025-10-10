#!/usr/bin/env bash
# Wait-for-HTTP Helper
# Wartet bis HTTP-Endpoint erreichbar ist

set -e

URL="$1"
TIMEOUT="${2:-120}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [timeout_seconds]"
  echo "Example: $0 http://localhost:8010/api/ 120"
  exit 1
fi

echo "Waiting for $URL (timeout: ${TIMEOUT}s)..."

for i in $(seq 1 "$TIMEOUT"); do
  if curl -fsS "$URL" >/dev/null 2>&1; then
    echo "✅ $URL is ready!"
    exit 0
  fi
  
  # Progress indicator
  if [ $((i % 10)) -eq 0 ]; then
    echo "Still waiting... (${i}s / ${TIMEOUT}s)"
  fi
  
  sleep 1
done

echo "❌ Timeout waiting for $URL after ${TIMEOUT}s" >&2
exit 1

