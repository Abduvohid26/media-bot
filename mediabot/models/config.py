import typing
import json

from mediabot.database.connection import acquire_connection

config_get_sql = open("mediabot/database/queries/config-get.sql").read()
config_set_sql = open("mediabot/database/queries/config-set.sql").read()

CONFIG_WEBAPP_URL = "WEBAPP_URL"

class Config:
  @staticmethod
  async def get_web_app_urls() -> typing.List[str]:
    params = {"config": CONFIG_WEBAPP_URL}
    async with acquire_connection() as conn:
      cursor = await conn.execute(config_get_sql, params)
      record = await cursor.fetchone()
      return json.loads(record["value"]) if record else []