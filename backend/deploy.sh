#!/bin/bash

if grep -q "8001" /etc/nginx/upstreams/template_active.conf; then
    TARGET_COLOR="green"
    TARGET_PORT="8002"
    OLD_COLOR="blue"
else
    TARGET_COLOR="blue"
    TARGET_PORT="8001"
    OLD_COLOR="green"
fi

echo "Deploying to $TARGET_COLOR slot on port $TARGET_PORT..."

docker compose up -d web-$TARGET_COLOR --build

echo "Waiting for health check..."
TIMEOUT=120
ELAPSED=0

CONTAINER=$(docker compose ps -q web-$TARGET_COLOR)
while [ "$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER")" != "healthy" ]; do
    printf "."
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo ""
        echo "ERROR: Container $CONTAINER did not become healthy within ${TIMEOUT}s. Aborting."
        exit 1
    fi
done


echo "server 127.0.0.1:$TARGET_PORT;" | sudo tee /etc/nginx/upstreams/template_active.conf
sudo nginx -s reload

echo "Traffic switched to $TARGET_COLOR."

docker compose stop web-$OLD_COLOR

docker compose down celery-worker celery-beat

docker compose up -d --build celery-worker celery-beat
