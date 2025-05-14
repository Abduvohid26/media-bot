import datetime
import typing
import psycopg.sql as sql
from enum import Enum
from mediabot.database.connection import acquire_connection

required_join_all_sql = open("mediabot/database/queries/required-join-all.sql").read()
required_join_sql = open("mediabot/database/queries/required-join.sql").read()
required_join_delete_sql = open("mediabot/database/queries/required-join-delete.sql").read()
required_join_update_sql = open("mediabot/database/queries/required-join-update.sql").read()
required_join_insert_sql = open("mediabot/database/queries/required-join-insert.sql").read()
required_join_all_for_sql = open("mediabot/database/queries/required-join-all-for.sql").read()
required_join_mark_insert_sql = open("mediabot/database/queries/required-join-mark-insert.sql").read()
required_join_for_join_sql = open("mediabot/database/queries/required-join-for-join.sql").read()
required_join_mark_has_joined_update_sql = open("mediabot/database/queries/required-join-mark-has-joined-update.sql").read()
required_join_after_join_message_all_sql = open("mediabot/database/queries/required-join-after-join-message-all.sql").read()
required_join_count_sql = open("mediabot/database/queries/required-join-count.sql").read()

CP_REQUIRED_JOIN_CURRENT_PAGE_CONTEXT = object()
CP_REQUIRED_JOIN_PER_PAGE_LIMIT = 10

REQUIRED_JOIN_STATE_EDIT_TARGET_COUNT_ENTER = object()
REQUIRED_JOIN_STATE_EDIT_SCHEDULE_COUNT_ENTER = object()
REQUIRED_JOIN_STATE_EDIT_JOIN_LINK_ENTER = object()
REQUIRED_JOIN_STATE_EDIT_TARGET_CHAT_ENTER = object()
REQUIRED_JOIN_STATE_EDIT_END_TIME_ENTER = object()

REQUIRED_JOIN_STATE_CREATE_TARGET_CHAT = object()

class RequiredJoinKind(Enum):
  MEDIA_QUERY = "MEDIA_QUERY"
  MEDIA_DOWNLOAD = "MEDIA_DOWNLOAD"

REQUIRED_JOIN_KINDS = [
  RequiredJoinKind.MEDIA_QUERY.value,
  RequiredJoinKind.MEDIA_DOWNLOAD.value
]

class _RequiredJoinFor:
  id: int
  target_chat: str
  join_link: typing.Union[str, None]
  messages: list[dict]
  has_mark: bool
  has_joined: bool
  instance_id: typing.Union[int, None]

  def to_json(self):
    return {
      "id": self.id,
      "target_chat": self.target_chat,
      "join_link": self.join_link,
      "messages": self.messages,
      "has_joined": self.has_joined
    }

class _RequiredJoin:
  id: int
  kind: str
  target_chat: str
  join_link: typing.Union[str, None]
  target_join_count: int
  is_enabled: bool
  is_optional: bool
  target_end_time: typing.Union[str, None]
  required_join_mark_count: int
  required_join_mark_has_joined_count: int
  created_at: str

class _RequiredJoinDetailed:
  id: int
  kind: str
  target_chat: str
  join_link: typing.Union[str, None]
  target_join_count: int
  is_enabled: bool
  is_optional: bool
  target_end_time: typing.Union[str, None]
  message_count: int
  required_join_mark_count: int
  required_join_mark_has_joined_count: int
  created_at: str

class _RequiredJoinAfterJoinMessage:
  message: dict
  is_forward: bool

class _RequiredJoinForJoin:
  id: int
  kind: str

class RequiredJoin:
  @staticmethod
  def deserialize(record: dict) -> _RequiredJoin:
    required_join = _RequiredJoin()

    required_join.id = record["id"]
    required_join.kind = record["kind"]
    required_join.target_chat = record["target_chat"]
    required_join.join_link = record["join_link"]
    required_join.target_join_count = record["target_join_count"]
    required_join.is_enabled = record["is_enabled"]
    required_join.is_optional = record["is_optional"]
    required_join.target_end_time = record["target_end_time"]
    required_join.required_join_mark_count = record["required_join_mark_count"]
    required_join.required_join_mark_has_joined_count = record["required_join_mark_has_joined_count"]
    required_join.created_at = record["created_at"]

    return required_join

  @staticmethod
  def deserialize_for_all(records: list[dict]) -> list[_RequiredJoinFor]:
    required_joins = {}

    for record in records:
      required_join = _RequiredJoinFor()
      required_join.id = record["required_join_id"]
      required_join.has_mark = record["required_join_has_mark"]
      required_join.has_joined = record["required_join_mark_has_joined"]
      required_join.join_link = record["required_join_join_link"]
      required_join.target_chat = record["required_join_target_chat"]
      required_join.instance_id = record["instance_id"]
      required_join.messages = []
      required_joins[required_join.id] = required_join

      for inner_record in records:
        if inner_record["required_join_id"] == record["required_join_id"] and record["required_join_message_message"]:
          required_join.messages.append(record["required_join_message_message"])

    return list(required_joins.values())

  @staticmethod
  def deserialize_detailed(record: dict) -> _RequiredJoinDetailed:
    required_join = _RequiredJoinDetailed()

    required_join.id = record["id"]
    required_join.kind = record["kind"]
    required_join.target_chat = record["target_chat"]
    required_join.join_link = record["join_link"]
    required_join.target_join_count = record["target_join_count"]
    required_join.is_enabled = record["is_enabled"]
    required_join.is_optional = record["is_optional"]
    required_join.target_end_time = record["target_end_time"]
    required_join.message_count = record["message_count"]
    required_join.required_join_mark_count = record["required_join_mark_count"]
    required_join.required_join_mark_has_joined_count = record["required_join_mark_has_joined_count"]
    required_join.created_at = record["created_at"]

    return required_join

  @staticmethod
  def deserialize_after_join_message(record: dict) -> _RequiredJoinAfterJoinMessage:
    message = _RequiredJoinAfterJoinMessage()

    message.message = record["message"]
    message.is_forward = record["is_forward"]

    return message

  @staticmethod
  def deserialize_for_join(record: dict) -> _RequiredJoinForJoin:
    required_join = _RequiredJoinForJoin()

    required_join.id = record["id"]
    required_join.kind = record["kind"]

    return required_join

  @staticmethod
  async def get_all(instance_origin: int) -> list[_RequiredJoin]:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_all_sql, params)
      records = await cursor.fetchall()
      return [RequiredJoin.deserialize(record) for record in records]

  @staticmethod
  async def get(required_join_id: int) -> typing.Union[_RequiredJoinDetailed, None]:
    params = {"required_join_id": required_join_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_sql, params)
      record = await cursor.fetchone()
      return RequiredJoin.deserialize_detailed(record) if record else None

  @staticmethod
  async def delete(required_join_id: int) -> None:
    params = {"required_join_id": required_join_id}
    async with acquire_connection() as conn:
      await conn.execute(required_join_delete_sql, params)

  @staticmethod
  async def update(required_join_id: int, fields: dict) -> None:
    update_fields = sql.SQL(", ").join([
      sql.Composed([sql.SQL(field), sql.SQL("="), sql.Literal(fields[field])])
          for field in fields.keys()
    ])

    params = {"required_join_id": required_join_id}
    query = sql.SQL(required_join_update_sql).format(update_fields)
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def update_is_optional(required_join_id: int, is_optional: bool) -> None:
    await RequiredJoin.update(required_join_id, {"is_optional": is_optional})

  @staticmethod
  async def update_is_enabled(required_join_id: int, is_enabled: bool) -> None:
    await RequiredJoin.update(required_join_id, {"is_enabled": is_enabled})

  @staticmethod
  async def update_target_join_count(required_join_id: int, target_join_count: int) -> None:
    await RequiredJoin.update(required_join_id, {"target_join_count": target_join_count})

  @staticmethod
  async def update_schedule_count(required_join_id: int, schedule_count: int) -> None:
    await RequiredJoin.update(required_join_id, {"schedule_count": schedule_count})

  @staticmethod
  async def update_kind(required_join_id: int, kind: str) -> None:
    await RequiredJoin.update(required_join_id, {"kind": kind})

  @staticmethod
  async def update_join_link(required_join_id: int, join_link: str) -> None:
    await RequiredJoin.update(required_join_id, {"join_link": join_link})

  @staticmethod
  async def update_target_chat(required_join_id: int, target_chat: str) -> None:
    await RequiredJoin.update(required_join_id, {"target_chat": target_chat})

  @staticmethod
  async def update_target_end_time(required_join_id: int, end_time: datetime.datetime) -> None:
    await RequiredJoin.update(required_join_id, {"target_end_time": end_time})

  @staticmethod
  async def get_all_for(instance_origin: int, account_origin: int, account_language_origin: typing.Union[int, None], kind: str) -> list[_RequiredJoinFor]:
    params = {
      "instance_origin": instance_origin,
      "account_origin": account_origin,
      "account_language_origin": account_language_origin,
      "kind": kind
    }

    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_all_for_sql, params)
      records = await cursor.fetchall()

      return RequiredJoin.deserialize_for_all(records)

  @staticmethod
  async def create_mark(instance_origin: int, required_join_origin: int, account_origin: int, has_joined: bool = False) -> None:
    params = {
      "instance_origin": instance_origin,
      "required_join_origin": required_join_origin,
      "account_origin": account_origin,
      "has_joined": has_joined
    }
    async with acquire_connection() as conn:
      await conn.execute(required_join_mark_insert_sql, params)

  @staticmethod
  async def get_for_join(instance_origin: int, account_origin: int, target_chat: typing.Union[str, None], target_chat_id: typing.Union[int, None]) -> typing.Union[_RequiredJoinForJoin, None]:
    params = {
      "instance_origin": instance_origin,
      "account_origin": account_origin,
      "target_chat": target_chat,
      "target_chat_id": target_chat_id
    }
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_for_join_sql, params)
      record = await cursor.fetchone()
      return RequiredJoin.deserialize_for_join(record) if record else None

  @staticmethod
  async def set_mark_has_joined(required_join_origin: int, account_origin: int, has_joined: bool) -> None:
    params = {"required_join_origin": required_join_origin, "account_origin": account_origin, "has_joined": has_joined}
    async with acquire_connection() as conn:
      await conn.execute(required_join_mark_has_joined_update_sql, params)

  @staticmethod
  async def get_after_join_messages_for(required_join_origin: int, account_origin: int) -> list[_RequiredJoinAfterJoinMessage]:
    params = {"required_join_origin": required_join_origin, "account_origin": account_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_after_join_message_all_sql, params)
      records = await cursor.fetchall()

      return [RequiredJoin.deserialize_after_join_message(record) for record in records]

  @staticmethod
  async def create(instance_origin: int, target_chat: str) -> typing.Union[int, None]:
    params = {"instance_origin": instance_origin, "target_chat": target_chat}
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"] if record else None

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(required_join_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]
