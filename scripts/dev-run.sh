# uvicorn mediabot.main:http_server --reload --reload-dir mediabot --port 8080 --env-file .env --ws none --workers 10
# uvicorn mediabot.main:http_server --port 8080 --env-file .env --ws none --workers 10

export WEBHOOK_URL="https://exchanger.services/mediabot/instances/{}/webhook"
export MEDIA_SERVICE_BASE_URL=http://localhost:3030

export ACCESS_TOKEN=a0172b72e3ecb62efce1734bc21922ed

export DATABASE_CONNECTION_POOL_MIN_SIZE=4
export DATABASE_CONNECTION_POOL_MAX_SIZE=10
export DATABASE_CONNECTION_URL=postgresql://postgres:49yLujm8Tihy@localhost:5434/database

export PGADMIN_DEFAULT_EMAIL=mhw0@yahoo.com
export PGADMIN_DEFAULT_PASSWORD=zyLH296zj7rN

export PGDATA=/var/lib/postgresql/data
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="49yLujm8Tihy"

export B2_APPLICATION_KEY_ID=00281e769202dd80000000007
export B2_APPLICATION_KEY=K002ZiYRHtgUL3Q8N76rx4JVJFiPHd0

gunicorn \
    --worker-class aiohttp.GunicornWebWorker \
    --bind 0.0.0.0:8080 \
    --backlog 10 \
    --worker-connections 10000 \
    --max-requests 1000 \
    --graceful-timeout 5 \
    --worker-tmp-dir /tmp \
    --reload \
    mediabot.main:http_server

    # --worker-class uvicorn.workers.UvicornWorker \
    # --keep-alive 1 \
    # --env .env \
