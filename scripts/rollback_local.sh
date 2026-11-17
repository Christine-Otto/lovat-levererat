#!/bin/bash
set -e

STABLE="1.0.0"
CONTAINER="leveransdatum"

echo "=== Starting rollback to version $STABLE ==="

echo "Checking that the previous version exists..."
docker image inspect "$CONTAINER:$STABLE" > /dev/null

echo "Removing current container if it exists..."
if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  docker rm -f "$CONTAINER"
fi

echo "Restoring previous version..."
docker run -d --name "$CONTAINER" -p 8000:8000 "$CONTAINER:$STABLE"

echo "Verifying rollback..."
bash scripts/verify.sh "$STABLE"

echo "Running image:"
docker inspect --format '{{.Config.Image}}' "$CONTAINER"

echo "=== Rollback completed ==="