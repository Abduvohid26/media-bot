from mediabot.cache import redis




class ClientManager:
    @staticmethod
    async def set_client_pending(client_id, ttl=60):
        await redis.set(f"client:pending:{client_id}", "is_job", ex=ttl)

    @staticmethod
    async def delete_client_pending(client_id):
        await redis.delete(f"client:pending:{client_id}")

    @staticmethod
    async def is_client_pending(client_id):
        return await redis.exists(f"client:pending:{client_id}")
