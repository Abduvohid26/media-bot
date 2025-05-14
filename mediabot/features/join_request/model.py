import typing
import psycopg.sql as sql
from mediabot.database.connection import acquire_connection

join_request_chat_all_sql = open("mediabot/database/queries/join-request-chat-all.sql").read()
join_request_chat_sql = open("mediabot/database/queries/join-request-chat.sql").read()
join_request_chat_by_chat_sql = open("mediabot/database/queries/join-request-chat-by-chat.sql").read()
join_request_delete_all_sql = open("mediabot/database/queries/join-request-delete-all.sql").read()
join_request_chat_delete_sql = open("mediabot/database/queries/join-request-chat-delete.sql").read()
join_request_chat_create_sql = open("mediabot/database/queries/join-request-chat-create.sql").read()
join_request_insert_sql = open("mediabot/database/queries/join-request-insert.sql").read()
join_request_chat_update_sql = open("mediabot/database/queries/join-request-chat-update.sql").read()
join_request_chat_count_sql = open("mediabot/database/queries/join-request-chat-count.sql").read()
join_request_by_cursor_sql = open("mediabot/database/queries/join-request-by-cursor.sql").read()
join_request_delete_many_sql = open("mediabot/database/queries/join-request-delete-many.sql").read()

JOIN_REQUEST_STATE_CREATE = object()

class _JoinRequestChat:
  id: int
  chat: str
  join_request_count: int
  message_count: int
  cursor: int
  is_autoapprove: bool
  is_autodecline: bool
  created_at: str

class _JoinRequestChatForJoin:
  id: int
  is_autoapprove: bool
  is_autodecline: bool
  messages: list[dict]

class _JoinRequestByCursor:
  id: int
  user_id: int

class JoinRequest:
  @staticmethod
  def deserialize_chat(record: dict) -> _JoinRequestChat:
    join_request_chat = _JoinRequestChat()

    join_request_chat.id = record["join_request_chat_id"]
    join_request_chat.chat = record["join_request_chat_chat"]
    join_request_chat.created_at = record["join_request_chat_created_at"]
    join_request_chat.join_request_count = record["join_request_count"]
    join_request_chat.is_autoapprove = record["join_request_chat_is_autoapprove"]
    join_request_chat.is_autodecline = record["join_request_chat_is_autodecline"]
    join_request_chat.message_count = record["join_request_chat_message_count"]
    join_request_chat.cursor = record["join_request_chat_cursor"]

    return join_request_chat

  @staticmethod
  def deserialize_chat_for_join(records: list[dict]) -> _JoinRequestChatForJoin:
    join_request_chat = _JoinRequestChatForJoin()

    join_request_chat.id = records[0]["join_request_chat_id"]
    join_request_chat.is_autoapprove = records[0]["join_request_chat_is_autoapprove"]
    join_request_chat.is_autodecline = records[0]["join_request_chat_is_autodecline"]
    join_request_chat.messages = [record["join_request_chat_message"] for record in records]

    return join_request_chat

  @staticmethod
  def deserialize_by_cursor(record: dict) -> _JoinRequestByCursor:
    join_request = _JoinRequestByCursor()

    join_request.id = record["id"]
    join_request.user_id = record["user_id"]

    return join_request

  @staticmethod
  async def get_chats(instance_origin: int) -> list[_JoinRequestChat]:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_chat_all_sql, params)
      records = await cursor.fetchall()

      return [JoinRequest.deserialize_chat(record) for record in records]

  # TODO(mhw0): add instance_origin too
  @staticmethod
  async def get_chat(join_request_chat_id: int) -> typing.Union[_JoinRequestChat, None]:
    params = {"join_request_chat_id": join_request_chat_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_chat_sql, params)
      record = await cursor.fetchone()

      return JoinRequest.deserialize_chat(record) if record else None

  @staticmethod
  async def get_chat_by_chat_for_join(instance_origin: int, join_request_chat: str, language_code: typing.Union[str, None]) -> typing.Union[_JoinRequestChatForJoin, None]:
    params = {
      "instance_origin": instance_origin,
      "join_request_chat": join_request_chat,
      "language_code": language_code
    }

    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_chat_by_chat_sql, params)
      records = await cursor.fetchall()

      return JoinRequest.deserialize_chat_for_join(records) if records else None

  @staticmethod
  async def delete_join_requests(join_request_chat_origin: int) -> None:
    params = {"join_request_chat_origin": join_request_chat_origin}
    async with acquire_connection() as conn:
      await conn.execute(join_request_delete_all_sql, params)

  @staticmethod
  async def delete_chat(join_request_chat_id: int) -> None:
    params = {"join_request_chat_id": join_request_chat_id}
    async with acquire_connection() as conn:
      await conn.execute(join_request_chat_delete_sql, params)

  @staticmethod
  async def create_chat(instance_origin: int, chat: str) -> int:
    params = {"instance_origin": instance_origin, "chat": chat}
    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_chat_create_sql, params)
      record = await cursor.fetchone()
      return int(record["id"])

  @staticmethod
  async def create_join_request(instance_origin: int, join_request_chat_origin: int, user_id: int) -> None:
    params = {"instance_origin": instance_origin, "join_request_chat_origin": join_request_chat_origin, "user_id": user_id}
    async with acquire_connection() as conn:
      await conn.execute(join_request_insert_sql, params)

  @staticmethod
  async def update_chat(join_request_chat_id: int, fields: dict) -> None:
    update_fields = sql.SQL(", ").join([
      sql.Composed([sql.SQL(field), sql.SQL("="), sql.Literal(fields[field])])
          for field in fields.keys()
    ])

    params = {"join_request_chat_id": join_request_chat_id}
    query = sql.SQL(join_request_chat_update_sql).format(update_fields)
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def update_chat_is_autoapprove(join_request_chat_id: int, is_autoapprove: bool) -> None:
    fields = {"is_autoapprove": is_autoapprove}
    await JoinRequest.update_chat(join_request_chat_id, fields)

  @staticmethod
  async def update_chat_is_autodecline(join_request_chat_id: int, is_autodecline: bool) -> None:
    fields = {"is_autodecline": is_autodecline}
    await JoinRequest.update_chat(join_request_chat_id, fields)

  @staticmethod
  async def update_cursor(join_request_chat_id: int, cursor: int) -> None:
    fields = {"cursor": cursor}
    await JoinRequest.update_chat(join_request_chat_id, fields)

  @staticmethod
  async def chat_count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_chat_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]

  @staticmethod
  async def get_join_request_by_cursor(join_request_chat_origin: int, cursor: int, limit: int) -> list[_JoinRequestByCursor]:
    params = {"join_request_chat_origin": join_request_chat_origin, "cursor": cursor, "limit": limit}
    async with acquire_connection() as conn:
      cursor = await conn.execute(join_request_by_cursor_sql, params)
      records = await cursor.fetchall()
      return [JoinRequest.deserialize_by_cursor(record) for record in records]

  @staticmethod
  async def delete_many(join_request_id_list: list[int]):
    account_id_sql = sql.SQL(", ").join([sql.Literal(join_request_id) for join_request_id in join_request_id_list])
    query = sql.SQL(join_request_delete_many_sql).format(account_id_sql)

    async with acquire_connection() as conn:
      await conn.execute(query)