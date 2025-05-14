from redis.asyncio import Redis
from mediabot.env import REDIS_HOST, REDIS_PORT, REDIS_MAX_CONNECTIONS

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)