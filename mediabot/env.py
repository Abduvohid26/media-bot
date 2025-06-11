import os

SERVER_BASE_URL = str(os.environ.get("SERVER_BASE_URL", ""))

MEDIA_SERVICE_BASE_URL = str(os.environ.get("MEDIA_SERVICE_BASE_URL", ""))

TELEGRAM_BOT_API_BASE_URL = str(os.environ.get("TELEGRAM_BOT_API_BASE_URL", ""))

API_ACCESS_TOKEN = str(os.environ.get("API_ACCESS_TOKEN", ""))

TELEGRAM_BOT_WEBHOOK_URL = str(os.environ.get("TELEGRAM_BOT_WEBHOOK_URL", ""))

DATABASE_CONNECTION_URL = os.environ.get("DATABASE_CONNECTION_URL", "")
DATABASE_CONNECTION_POOL_MIN_SIZE = int(os.environ.get("DATABASE_CONNECTION_POOL_MIN_SIZE", 10))
DATABASE_CONNECTION_POOL_MAX_SIZE = int(os.environ.get("DATABASE_CONNECTION_POOL_MAX_SIZE", 20))

CONCURRENT_UPDATES = int(os.environ.get("CONCURRENT_UPDATES", 30))

REDIS_HOST = str(os.environ.get("REDIS_HOST", "redis"))
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_MAX_CONNECTIONS = int(os.environ.get("REDIS_MAX_CONNECTIONS", 100))

TELEGRAM_PATH = str(os.environ.get("TELEGRAM_PATH", ""))

CENTRAL_BOT_API = str(os.environ.get("CENTRAL_BOT_API", ""))