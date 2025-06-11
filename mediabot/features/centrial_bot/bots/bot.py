

from mediabot.database.connection import acquire_connection




async def all_bot_username():
    query = 'SELECT username FROM "instance";'
    async with acquire_connection() as conn:
        cursor = await conn.execute(query)
        records = await cursor.fetchall()
        return records


