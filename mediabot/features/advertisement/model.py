import typing
import psycopg.sql as sql
from mediabot.database.connection import acquire_connection

advertisement_all_sql = open("mediabot/database/queries/advertisement-all.sql").read()
advertisement_sql = open("mediabot/database/queries/advertisement.sql").read()
advertisement_delete_sql = open("mediabot/database/queries/advertisement-delete.sql").read()
advertisement_update_sql = open("mediabot/database/queries/advertisement-update.sql").read()
advertisement_message_all_for_sql = open("mediabot/database/queries/advertisement-message-all-for.sql").read()
advertisement_message_seen_clear_sql = open("mediabot/database/queries/advertisement-message-seen-clear.sql").read()
advertisement_insert_sql = open("mediabot/database/queries/advertisement-insert.sql").read()
advertisement_count_sql = open("mediabot/database/queries/advertisement-count.sql").read()

ADVERTISEMENT_STATE_CREATE_NAME = object()

class _Advertisement:
  id: int
  name: str
  kind: int
  is_enabled: bool
  message_count: int
  message_seen_count: int
  created_at: str

class _AdvertisementMessageFor:
  id: int
  message: dict
  is_attach: bool
  is_onetime: bool
  is_forward: bool
  is_seen: bool

  def to_json(self):
    return {
      "id": self.id,
      "message": self.message,
      "is_attach": self.is_attach,
      "is_onetime": self.is_onetime,
      "is_forward": self.is_forward,
      "is_seen": self.is_seen
    }

class Advertisement:
  KIND_NONE = None
  KIND_PHOTO = 1
  KIND_VIDEO = 2
  KIND_AUDIO = 3
  KIND_VOICE = 4
  KIND_TRACK_SEARCH = 5
  KIND_YOUTUBE_SEARCH = 6

  KINDS = [KIND_NONE, KIND_PHOTO, KIND_VIDEO, KIND_AUDIO, KIND_VOICE, KIND_TRACK_SEARCH, KIND_YOUTUBE_SEARCH]

  @staticmethod
  def stringify_kind(kind: typing.Union[int, None]) -> str:
    if kind == Advertisement.KIND_NONE:
      return "-"
    elif kind == Advertisement.KIND_PHOTO:
      return "🖼 Photo"
    elif kind == Advertisement.KIND_VIDEO:
      return "🎞 Video"
    elif kind == Advertisement.KIND_AUDIO:
      return "🎧 Audio"
    elif kind == Advertisement.KIND_VOICE:
      return "🎙 Voice"
    elif kind == Advertisement.KIND_TRACK_SEARCH:
      return "🔍 Track search"
    elif kind == Advertisement.KIND_YOUTUBE_SEARCH:
      return "🎞 YouTube search"
    
    return "-"

  @staticmethod
  def deserialize(record: dict) -> _Advertisement:
    advertisement = _Advertisement()

    advertisement.id = record["advertisement_id"]
    advertisement.name = record["advertisement_name"]
    advertisement.kind = record["advertisement_kind"]
    advertisement.is_enabled = record["advertisement_is_enabled"]
    advertisement.created_at = record["advertisement_created_at"]
    advertisement.message_count = record["advertisement_message_count"]
    advertisement.message_seen_count = record["advertisement_message_seen_count"]

    return advertisement

  @staticmethod
  def deserialize_message_for(record: dict) -> _AdvertisementMessageFor:
    message = _AdvertisementMessageFor()

    message.id = record["id"]
    message.message = record["message"]
    message.is_attach = record["is_attach"]
    message.is_onetime = record["is_onetime"]
    message.is_forward = record["is_forward"]
    message.is_seen = record["is_seen"]

    return message

  @staticmethod
  async def get_all(instance_origin: int, offset: int = 0, limit: int = 0) -> list[_Advertisement]:
    params = {"instance_origin": instance_origin, "offset": offset, "limit": limit}
    async with acquire_connection() as conn:
      cursor = await conn.execute(advertisement_all_sql, params)
      records = await cursor.fetchall()

      return [Advertisement.deserialize(record) for record in records]

  @staticmethod
  async def get(advertisement_id: int) -> typing.Union[_Advertisement, None]:
    params = {"advertisement_id": advertisement_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(advertisement_sql, params)
      record = await cursor.fetchone()

      return Advertisement.deserialize(record) if record else None

  @staticmethod
  async def delete(advertisement_id: int) -> None:
    params = {"advertisement_id": advertisement_id}
    async with acquire_connection() as conn:
      await conn.execute(advertisement_delete_sql, params)

  @staticmethod
  async def update(advertisement_id: int, fields: dict) -> None:
    update_fields = sql.SQL(", ").join([
      sql.Composed([sql.SQL(field), sql.SQL("="), sql.Literal(fields[field])])
          for field in fields.keys()
    ])

    params = {"advertisement_id": advertisement_id}
    query = sql.SQL(advertisement_update_sql).format(update_fields)
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def update_is_enabled(advertisement_id: int, is_enabled: bool) -> None:
    fields = {"is_enabled": is_enabled}
    await Advertisement.update(advertisement_id, fields)

  @staticmethod
  async def update_kind(advertisement_id: int, kind: int) -> None:
    fields = {"kind": kind}
    await Advertisement.update(advertisement_id, fields)

  @staticmethod
  async def get_all_messages_for(instance_origin: int, kind: int, account_origin: int) -> list[_AdvertisementMessageFor]:
    params = {"instance_origin": instance_origin, "kind": kind, "account_origin": account_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(advertisement_message_all_for_sql, params)
      records = await cursor.fetchall()

      return [Advertisement.deserialize_message_for(record) for record in records]

  @staticmethod
  async def clear_message_seen(advertisement_origin: int) -> None:
    params = {"advertisement_origin": advertisement_origin}
    async with acquire_connection() as conn:
      await conn.execute(advertisement_message_seen_clear_sql, params)

  @staticmethod
  async def create(instance_origin: int, name: str) -> None:
    params = {"instance_origin": instance_origin, "name": name, "kind": Advertisement.KIND_NONE}
    async with acquire_connection() as conn:
      cursor = await conn.execute(advertisement_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"]

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(advertisement_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]
