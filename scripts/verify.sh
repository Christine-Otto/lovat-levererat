#!/bin/bash
set -e

URL="http://localhost:8000"
VERSION="${1:-1.0.0}"

echo "=== Verifying deployment ==="

for i in {1..10}; do
  if curl --fail --silent "$URL/health" > /dev/null; then
    echo "Health OK"
    break
  fi
  echo "Waiting for application..."
  sleep 2
  if [ "$i" -eq 10 ]; then
    echo "Health check failed"
    exit 1
  fi
done

echo "Checking version..."
curl --fail --silent "$URL/version" | grep -q "\"version\":\"$VERSION\"" \
  || { echo "Wrong version (expected $VERSION)"; exit 1; }
echo "Version $VERSION OK"

echo "Checking delivery date (express, Friday -> Monday)..."
curl --fail --silent "$URL/leveransdatum?orderdatum=2026-11-20&tid=09:00&alternativ=express" \
  | grep -q '"leveransdatum":"2026-11-23"' \
  || { echo "Wrong delivery date"; exit 1; }
echo "Delivery date OK"

echo "Deployment verified successfully"
