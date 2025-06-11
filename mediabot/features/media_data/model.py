from mediabot.database.connection import acquire_connection



class MediaDataBase:
    @staticmethod
    async def get_media_by_link(link: str, bot_token: str):
        params = {"link": link}
        query = "SELECT * FROM media_data WHERE link = %(link)s;"
        async with acquire_connection() as connection:
            cursor = await connection.execute(query, params)
            media_data = await cursor.fetchone()
            if media_data is None:
                return None, False
            if media_data.get('bot_token') == bot_token:
                return media_data, True
            else:
                return media_data, False
            

    @staticmethod
    async def add_media_data(platform: str, link: str, file_id: str, caption: str = None, bot_token: str = None, bot_username: str = None):
        params = {
            "platform": platform,
            "link": link,
            "file_id": file_id,
            "caption": caption,
            "bot_token": bot_token,
            "bot_username": bot_username
        }
        query = """
        INSERT INTO media_data (platform, link, file_id, caption, bot_token, bot_username)
        VALUES (%(platform)s, %(link)s, %(file_id)s, %(caption)s, %(bot_token)s, %(bot_username)s)
        ON CONFLICT (link) DO NOTHING;
        """
        async with acquire_connection() as connection:
            await connection.execute(query, params)


    