#!/bin/bash
set -e

VERSION="${1:-1.0.0}"
CONTAINER="leveransdatum"

echo "=== Starting local deployment of version $VERSION ==="

echo "Building Docker image..."
docker build -t "$CONTAINER:$VERSION" .

echo "Removing previous container if it exists..."
if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  docker rm -f "$CONTAINER"
fi

echo "Checking that port 8000 is free..."
if docker ps --format '{{.Ports}}' | grep -q ':8000->'; then
  echo "Port 8000 is used by another container:"
  docker ps
  exit 1
fi

echo "Starting application..."
docker run -d --name "$CONTAINER" -p 8000:8000 "$CONTAINER:$VERSION"

echo "=== Deployment started ==="