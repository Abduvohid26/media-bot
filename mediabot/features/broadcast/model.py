import typing

from mediabot.database.connection import acquire_connection
from mediabot.cache import redis

broadcast_create_sql = open("mediabot/database/queries/broadcast-create.sql").read()
broadcast_all_sql = open("mediabot/database/queries/broadcast-all.sql").read()
broadcast_sql = open("mediabot/database/queries/broadcast.sql").read()
broadcast_delete_sql = open("mediabot/database/queries/broadcast-delete.sql").read()
broadcast_set_is_running_sql = open("mediabot/database/queries/broadcast-set-is-running.sql").read()
broadcast_state_update_sql = open("mediabot/database/queries/broadcast-state-update.sql").read()
broadcast_count_sql = open("mediabot/database/queries/broadcast-count.sql").read()

BROADCAST_ACCOUNT_COUNT_PER_ITER = 25
BROADCAST_GROUP_COUNT_PER_ITER = 20

BROADCAST_STATE_CREATE_NAME = object()
BROADCAST_STATE_CREATE_MESSAGE = object()
BROADCAST_STATE_CREATE_LANGUAGE = object()
BROADCAST_STATE_CREATE_JOBS = object()
BROADCAST_STATE_CREATE_IS_GROUP = object()
BROADCAST_STATE_CREATE_IS_SILENT = object()

class _MessageLanguage:
  id: int
  code: str
  name: str

class _Message:
  id: int
  message: dict
  language: typing.Union[_MessageLanguage, None]

class _Broadcast:
  id: int
  name: str
  is_running: int
  is_group: bool
  is_silent: bool
  mps: int
  jobs: int
  cursor: int
  eta: int
  succeeded_jobs: int
  failed_jobs: int
  blocked_jobs: int
  message: _Message
  created_at: str

class Broadcast:
  @staticmethod
  def deserialize(record: dict) -> _Broadcast:
    broadcast = _Broadcast()

    broadcast.id = record["broadcast_id"]
    broadcast.name = record["broadcast_name"]
    broadcast.is_running = record["broadcast_is_running"]
    broadcast.is_group = record["broadcast_is_group"]
    broadcast.is_silent = record["broadcast_is_silent"]
    broadcast.mps = record["broadcast_mps"]
    broadcast.jobs = record["broadcast_jobs"]
    broadcast.cursor = record["broadcast_cursor"]
    broadcast.eta = record["broadcast_eta"]
    broadcast.succeeded_jobs = record["broadcast_succeeded_jobs"]
    broadcast.failed_jobs = record["broadcast_failed_jobs"]
    broadcast.blocked_jobs = record["broadcast_blocked_jobs"]
    broadcast.message = _Message()
    broadcast.message.id = record["broadcast_message_id"]
    broadcast.message.message = record["broadcast_message_message"]
    broadcast.message.language = None
    if record["broadcast_message_language_id"]:
      broadcast.message.language = _MessageLanguage()
      broadcast.message.language.id = record["broadcast_message_language_id"]
      broadcast.message.language.code = record["broadcast_message_language_code"]
      broadcast.message.language.name = record["broadcast_message_language_name"]
    broadcast.created_at = record["broadcast_created_at"]

    return broadcast

  @staticmethod
  async def create(instance_origin: int, name: str, message: str, jobs: int, is_group: bool, is_silent: bool, language_origin: int) -> None:
    params = {
      "name": name,
      "message": message,
      "jobs": jobs,
      "is_group": is_group,
      "is_silent": is_silent,
      "language_origin": language_origin,
      "instance_origin": instance_origin
    }

    async with acquire_connection() as conn:
      cursor = await conn.execute(broadcast_create_sql, params)
      record = await cursor.fetchone()
      return record["id"]

  @staticmethod
  async def get_all(instance_origin: int) -> list[_Broadcast]:
    params = {"instance_origin": instance_origin}

    async with acquire_connection() as conn:
      cursor = await conn.execute(broadcast_all_sql, params)
      records = await cursor.fetchall()

      return [Broadcast.deserialize(record) for record in records]

  @staticmethod
  async def get(broadcast_id: int) -> typing.Union[_Broadcast, None]:
    params = {"broadcast_id": broadcast_id}

    async with acquire_connection() as conn:
      cursor = await conn.execute(broadcast_sql, params)
      record = await cursor.fetchone()

      return Broadcast.deserialize(record) if record else None

  @staticmethod
  async def delete(broadcast_id: int) -> typing.Union[_Broadcast, None]:
    params = {"broadcast_id": broadcast_id}

    async with acquire_connection() as conn:
      await conn.execute(broadcast_delete_sql, params)

  @staticmethod
  async def set_is_running(broadcast_id: int, is_running: bool) -> None:
    params = {"broadcast_id": broadcast_id, "is_running": is_running}

    async with acquire_connection() as conn:
      await conn.execute(broadcast_set_is_running_sql, params)

  @staticmethod
  async def update_state(
    broadcast_id: int,
    cursor: typing.Union[int, None] = None,
    succeeded_jobs: typing.Union[int, None] = None,
    failed_jobs: typing.Union[int, None] = None,
    blocked_jobs: typing.Union[int, None] = None
  ):
    params = {
      "broadcast_id": broadcast_id,
      "cursor": cursor,
      "succeeded_jobs": succeeded_jobs,
      "failed_jobs": failed_jobs,
      "blocked_jobs": blocked_jobs
    }

    async with acquire_connection() as conn:
      await conn.execute(broadcast_state_update_sql, params)

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(broadcast_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]


  @staticmethod
  async def append_sent_messages(instance_origin: int, broadcast_id: int, messages: list[int]):
    await redis.lpush(f"broadcast:message:{instance_origin}:{broadcast_id}", *(map(lambda message: f"{message[0]}:{message[1]}", messages)))

  @staticmethod
  async def get_sent_messages(instance_origin: int, broadcast_id: int, offset: int, limit: int):
    await redis.lrange(f"broadcast:message:{instance_origin}:{broadcast_id}", offset, limit)

  @staticmethod
  async def get_sent_message_cursor(instance_origin: int, broadcast_id: int):
    cursor = await redis.get(f"broadcast:message:cursor:{instance_origin}:{broadcast_id}")
    return int(cursor)

  @staticmethod
  async def set_sent_message_cursor(instance_origin: int, broadcast_id: int):
    await redis.set(f"broadcast:message:cursor:{instance_origin}:{broadcast_id}", str(broadcast_id))
