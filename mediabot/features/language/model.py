from mediabot.database.connection import acquire_connection

language_all_sql = open("mediabot/database/queries/language-all.sql").read()
language_insert_sql = open("mediabot/database/queries/language-insert.sql").read()
language_delete_sql = open("mediabot/database/queries/language-delete.sql").read()
language_count_sql = open("mediabot/database/queries/language-count.sql").read()

LANGUAGE_STATE_CREATE_NAME = object()
LANGUAGE_STATE_CREATE_CODE = object()

class _Language:
  id: int
  code: str
  name: str

class Language:
  @staticmethod
  def deserialize(record: dict) -> _Language:
    language = _Language()
    language.id = record["id"]
    language.code = record["code"]
    language.name = record["name"]
    return language

  @staticmethod
  async def get_all(instance_origin: int) -> list[_Language]:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(language_all_sql, params)
      records = await cursor.fetchall()
      return [Language.deserialize(record) for record in records]

  @staticmethod
  async def create(instance_origin: int, name: str, code: str) -> None:
    params = {"instance_origin": instance_origin, "name": name, "code": code}
    async with acquire_connection() as conn:
      await conn.execute(language_insert_sql, params)

  @staticmethod
  async def delete(language_id: int) -> None:
    params = {"language_id": language_id}
    async with acquire_connection() as conn:
      await conn.execute(language_delete_sql, params)

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(language_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]
