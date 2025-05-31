from mediabot.database.connection import acquire_connection



media_get_sql = open("mediabot/database/queries/media-data-by-file_id.sql").read()
media_insert_sql = open("mediabot/database/queries/media-data-insert.sql").read()


class MedidaData:
    @staticmethod
    async def get_media_by_file_id(file_id: str):
        params = {"file_id": file_id}
        async with acquire_connection() as connection:
            cursor = await connection.execute(media_get_sql, params)
            media_data = await cursor.fetchone()
            return media_data

    @staticmethod
    async def media_data_insert(platform: str, link: str, file_id: str, caption: str = None):
        params = {"platform": platform, "link": link, "file_id": file_id, "caption": caption}
        async with acquire_connection() as connection:
            await connection.execute(media_insert_sql, params)



