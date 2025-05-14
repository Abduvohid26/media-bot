import typing
import time
import psycopg.sql as sql
import datetime
from enum import Enum
from mediabot.database.connection import acquire_connection
from mediabot.cache import redis

instance_all_sql = open("mediabot/database/queries/instance-all.sql").read()
instance_sql = open("mediabot/database/queries/instance.sql").read()
instance_by_token_sql = open("mediabot/database/queries/instance-by-token.sql").read()
instance_insert_sql = open("mediabot/database/queries/instance-insert.sql").read()
# instance_update_sql = open("mediabot/database/queries/instance-update.sql").read()
instance_quota_used_increment_sql = open("mediabot/database/queries/instance-quota-used-increment.sql").read()
instance = open("mediabot/database/queries/instance.sql").read()
instance_enable_sql = open("mediabot/database/queries/instance-enable.sql").read()
instance_disable_sql = open("mediabot/database/queries/instance-disable.sql").read()
instance_feature_update_sql = open("mediabot/database/queries/instance-feature-update.sql").read()
instance_exists_by_token_sql = open("mediabot/database/queries/instance-exists-by-token.sql").read()

INSTANCE_ID_CONTEXT = object()
INSTANCE_CONTEXT = object()
INSTANCE_REQUEST_RATE_LIMITER_CONTEXT = object()
INSTANCE_LOGGER_CONTEXT = object()

class InstanceFeatures(Enum):
  # def __str__(self):
  #   return str(self.value.lower())

  TRACK = "track_feature_enabled"
  TRACK_SEARCH = "track_search_feature_enabled"
  TRACK_DOWNLOAD = "track_download_feature_enabled"
  TRACK_RECOGNIZE_FROM_VOICE = "track_recognize_from_voice_feature_enabled"
  TRACK_RECOGNIZE_FROM_VIDEO_NOTE = "track_recognize_from_video_note_feature_enabled"
  TRACK_RECOGNIZE_FROM_AUDIO = "track_recognize_from_audio_feature_enabled"
  TRACK_RECOGNIZE_FROM_VIDEO = "track_recognize_from_video_feature_enabled"

  YOUTUBE = "youtube_feature_enabled"
  YOUTUBE_SEARCH = "youtube_search_feature_enabled"
  YOUTUBE_DOWNLOAD = "youtube_download_feature_enabled"
  YOUTUBE_LINK = "youtube_link_feature_enabled"
  YOUTUBE_RECOGNIZE_TRACK = "youtube_recognize_track_feature_enabled"

  TIKTOK = "tiktok_feature_enabled"
  TIKTOK_RECOGNIZE_TRACK = "tiktok_recognize_track_feature_enabled"

  INSTAGRAM = "instagram_feature_enabled"
  INSTAGRAM_RECOGNIZE_TRACK = "instagram_recognize_track_feature_enabled"

  TWITTER = "twitter_feature_enabled"
  LIKEE = "likee_feature_enabled"
  TUMBLR = "tumblr_feature_enabled"
  PINTEREST = "pinterest_feature_enabled"
  FACEBOOK = "facebook_feature_enabled"

  BROADCAST = "broadcast_feature_enabled"
  COMMAND = "command_feature_enabled"
  REQUIRED_JOIN = "required_join_feature_enabled"
  ADVERTISEMENT = "advertisement_feature_enabled"
  JOIN_REQUEST = "join_request_feature_enabled"
  REFERRAL = "referral_feature_enabled"
  MESSAGE = "message_feature_enabled"
  TRACK_POPULAR_TRACKS = "track_popular_tracks_feature_enabled"
  VIDEO_SEARCH = "video_search_feature_enabled"
  VIDEO_DOWNLOAD = "video_download_feature_enabled"
  WEB = "web_feature_enabled"

class InstanceQuota(Enum):
  def __str__(self):
    return str(self.value.lower())

  TRACK = "track_quota"
  INSTAGRAM = "instagram_quota"
  TIKTOK = "tiktok_quota"
  YOUTUBE = "youtube_quota"

class _Instance(object):
  id: int
  token: str
  username: str
  is_enabled: bool
  created_at: str
  actions_per_second: int
  is_web: bool

  track_search_feature_enabled: bool
  track_download_feature_enabled: bool
  track_recognize_from_voice_feature_enabled: bool
  track_recognize_from_video_note_feature_enabled: bool
  track_recognize_from_audio_feature_enabled: bool
  track_recognize_from_video_feature_enabled: bool
  track_quota: int
  track_used: int

  tiktok_feature_enabled: bool
  tiktok_recognize_track_feature_enabled: bool
  tiktok_quota: int
  tiktok_used: int

  instagram_feature_enabled: bool
  instagram_recognize_track_feature_enabled: bool
  instagram_quota: int
  instagram_used: int

  twitter_feature_enabled: bool
  likee_feature_enabled: bool
  tumblr_feature_enabled: bool
  pinterest_feature_enabled: bool
  facebook_feature_enabled: bool

  youtube_search_feature_enabled: bool
  youtube_download_feature_enabled: bool
  youtube_link_feature_enabled: bool
  youtube_recognize_track_feature_enabled: bool
  youtube_quota: int
  youtube_used: int

  broadcast_feature_enabled: bool
  command_feature_enabled: bool
  required_join_feature_enabled: bool
  advertisement_feature_enabled: bool
  join_request_feature_enabled: bool
  referral_feature_enabled: bool

  web_feature_enabled: bool

  def to_json(self) -> dict:
    return {
      "id": self.id,
      "token": self.token,
      "username": self.username,
      "is_enabled": self.is_enabled,
      "created_at": str(self.created_at),
      "actions_per_second": self.actions_per_second,
      # "is_web": self.is_web,

      "track_search_feature_enabled": self.track_search_feature_enabled,
      "track_download_feature_enabled": self.track_download_feature_enabled,
      "track_recognize_from_voice_feature_enabled": self.track_recognize_from_voice_feature_enabled,
      "track_recognize_from_video_note_feature_enabled": self.track_recognize_from_video_note_feature_enabled,
      "track_recognize_from_audio_feature_enabled": self.track_recognize_from_audio_feature_enabled,
      "track_recognize_from_video_feature_enabled": self.track_recognize_from_video_feature_enabled,
      "track_quota": self.track_quota,
      "track_used": self.track_used,

      "instagram_feature_enabled": self.instagram_feature_enabled,
      "instagram_recognize_track_feature_enabled": self.instagram_recognize_track_feature_enabled,
      "instagram_quota": self.instagram_quota,
      "instagram_used": self.instagram_used,

      "tiktok_feature_enabled": self.tiktok_feature_enabled,
      "tiktok_recognize_track_feature_enabled": self.tiktok_recognize_track_feature_enabled,
      "tiktok_quota": self.tiktok_quota,
      "tiktok_used": self.tiktok_used,

      "twitter_feature_enabled": self.twitter_feature_enabled,
      "likee_feature_enabled": self.likee_feature_enabled,
      "tumblr_feature_enabled": self.tumblr_feature_enabled,
      "pinterest_feature_enabled": self.pinterest_feature_enabled,
      "facebook_feature_enabled": self.facebook_feature_enabled,

      "youtube_search_feature_enabled": self.youtube_search_feature_enabled,
      "youtube_download_feature_enabled": self.youtube_download_feature_enabled,
      "youtube_link_feature_enabled": self.youtube_link_feature_enabled,
      "youtube_recognize_track_feature_enabled": self.youtube_recognize_track_feature_enabled,
      "youtube_quota": self.youtube_quota,
      "youtube_used": self.youtube_used,

      "broadcast_feature_enabled": self.broadcast_feature_enabled,
      "command_feature_enabled": self.command_feature_enabled,
      "required_join_feature_enabled": self.required_join_feature_enabled,
      "advertisement_feature_enabled": self.advertisement_feature_enabled,
      "join_request_feature_enabled": self.join_request_feature_enabled,
      "referral_feature_enabled": self.referral_feature_enabled,

      "web_feature_enabled": self.web_feature_enabled,
    }

class Instance:
  @staticmethod
  def deserialize(record: dict) -> _Instance:
    instance = _Instance()

    instance.id = record["instance_id"]
    instance.token = record["instance_token"]
    instance.username = record["instance_username"]
    instance.is_enabled = record["instance_is_enabled"]
    instance.created_at = record["instance_created_at"]
    instance.actions_per_second = record["instance_actions_per_second"]

    instance.track_search_feature_enabled = record["instance_track_search_feature_enabled"]
    instance.track_download_feature_enabled = record["instance_track_download_feature_enabled"]
    instance.track_recognize_from_voice_feature_enabled = record["instance_track_recognize_from_voice_feature_enabled"]
    instance.track_recognize_from_video_note_feature_enabled = record["instance_track_recognize_from_video_note_feature_enabled"]
    instance.track_recognize_from_audio_feature_enabled = record["instance_track_recognize_from_audio_feature_enabled"]
    instance.track_recognize_from_video_feature_enabled = record["instance_track_recognize_from_video_feature_enabled"]
    instance.track_quota = record["instance_track_quota"]
    instance.track_used = record["instance_track_used"]

    instance.instagram_feature_enabled = record["instance_instagram_feature_enabled"]
    instance.instagram_recognize_track_feature_enabled = record["instance_instagram_recognize_track_feature_enabled"]
    instance.instagram_quota = record["instance_instagram_quota"]
    instance.instagram_used = record["instance_instagram_used"]

    instance.tiktok_feature_enabled = record["instance_tiktok_feature_enabled"]
    instance.tiktok_recognize_track_feature_enabled = record["instance_tiktok_recognize_track_feature_enabled"]
    instance.tiktok_quota = record["instance_tiktok_quota"]
    instance.tiktok_used = record["instance_tiktok_used"]
    instance.tiktok_recognize_track_feature_enabled = record["instance_tiktok_recognize_track_feature_enabled"]

    instance.twitter_feature_enabled = record["instance_twitter_feature_enabled"]
    instance.likee_feature_enabled = record["instance_likee_feature_enabled"]
    instance.tumblr_feature_enabled = record["instance_tumblr_feature_enabled"]
    instance.pinterest_feature_enabled = record["instance_pinterest_feature_enabled"]
    instance.facebook_feature_enabled = record["instance_facebook_feature_enabled"]

    instance.youtube_search_feature_enabled = record["instance_youtube_search_feature_enabled"]
    instance.youtube_download_feature_enabled = record["instance_youtube_download_feature_enabled"]
    instance.youtube_link_feature_enabled = record["instance_youtube_link_feature_enabled"]
    instance.youtube_recognize_track_feature_enabled = record["instance_youtube_recognize_track_feature_enabled"]
    instance.youtube_quota = record["instance_youtube_quota"]
    instance.youtube_used = record["instance_youtube_used"]

    instance.broadcast_feature_enabled = record["instance_broadcast_feature_enabled"]
    instance.command_feature_enabled = record["instance_command_feature_enabled"]
    instance.required_join_feature_enabled = record["instance_required_join_feature_enabled"]
    instance.advertisement_feature_enabled = record["instance_advertisement_feature_enabled"]
    instance.join_request_feature_enabled = record["instance_join_request_feature_enabled"]
    instance.referral_feature_enabled = record["instance_referral_feature_enabled"]

    instance.web_feature_enabled = record["instance_web_feature_enabled"]

    return instance

  @staticmethod
  async def get(instance_id: int) -> typing.Union[_Instance, None]:
    params = {"instance_id": instance_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(instance_sql, params)
      record = await cursor.fetchone()
      return Instance.deserialize(record) if record else None

  @staticmethod
  async def get_by_token(token: str) -> typing.Union[_Instance, None]:
    params = {"token": token}
    async with acquire_connection() as conn:
      cursor = await conn.execute(instance_by_token_sql, params)
      record = await cursor.fetchone()
      return Instance.deserialize(record) if record else None

  @staticmethod
  async def get_all() -> list[_Instance]:
    async with acquire_connection() as conn:
      cursor = await conn.execute(instance_all_sql)
      records = await cursor.fetchall()
      return [Instance.deserialize(record) for record in records]

  @staticmethod
  async def increment_used(instance_origin: int, field: str) -> None:
    params = {"instance_origin": instance_origin}
    query = sql.SQL(instance_quota_used_increment_sql).format(sql.SQL(field))
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def increment_track_used(instance_origin: int) -> None:
    await Instance.increment_used(instance_origin, "track_used")

  @staticmethod
  async def increment_instagram_used(instance_origin: int) -> None:
    await Instance.increment_used(instance_origin, "instagram_used")

  @staticmethod
  async def increment_tiktok_used(instance_origin: int) -> None:
    await Instance.increment_used(instance_origin, "tiktok_used")

  @staticmethod
  async def increment_youtube_used(instance_origin: int) -> None:
    await Instance.increment_used(instance_origin, "youtube_used")

  @staticmethod
  async def enable_instance(instance_id: int) -> None:
    params = {"instance_id": instance_id}
    async with acquire_connection() as conn:
      await conn.execute(instance_enable_sql, params)

  @staticmethod
  async def disable_instance(instance_id: int) -> None:
    params = {"instance_id": instance_id}
    async with acquire_connection() as conn:
      await conn.execute(instance_disable_sql, params)

  @staticmethod
  async def create(
    token: str,
    username: str,

    track_search_feature_enabled: bool = False,
    track_download_feature_enabled: bool = False,
    track_recognize_from_voice_feature_enabled: bool = False,
    track_recognize_from_video_note_feature_enabled: bool = False,
    track_recognize_from_audio_feature_enabled: bool = False,
    track_recognize_from_video_feature_enabled: bool = False,
    track_quota: int = 100,

    instagram_feature_enabled: bool = False,
    instagram_recognize_track_feature_enabled: bool = False,
    instagram_quota: int = 100,

    tiktok_feature_enabled: bool = False,
    tiktok_recognize_track_feature_enabled: bool = False,
    tiktok_quota: int = 100,

    twitter_feature_enabled: bool = False,
    likee_feature_enabled: bool = False,
    tumblr_feature_enabled: bool = False,
    pinterest_feature_enabled: bool = False,
    facebook_feature_enabled: bool = False,

    youtube_search_feature_enabled: bool = False,
    youtube_download_feature_enabled: bool = False,
    youtube_recognize_track_feature_enabled: bool = False,
    youtube_quota: int = 100,

    broadcast_feature_enabled: bool = False,
    command_feature_enabled: bool = False,
    required_join_feature_enabled: bool = False,
    advertisement_feature_enabled: bool = False,
    referral_feature_enabled: bool = False,
    join_request_feature_enabled: bool = False,

    web_feature_enabled: bool = False
  ):
    params = {
      "token": token,
      "username": username,

      "track_search_feature_enabled": track_search_feature_enabled,
      "track_download_feature_enabled": track_download_feature_enabled,
      "track_recognize_from_voice_feature_enabled": track_recognize_from_voice_feature_enabled,
      "track_recognize_from_audio_feature_enabled": track_recognize_from_audio_feature_enabled,
      "track_recognize_from_video_note_feature_enabled": track_recognize_from_video_note_feature_enabled,
      "track_recognize_from_video_feature_enabled": track_recognize_from_video_feature_enabled,
      "track_quota": track_quota,

      "instagram_feature_enabled": instagram_feature_enabled,
      "instagram_recognize_track_feature_enabled": instagram_recognize_track_feature_enabled,
      "instagram_quota": instagram_quota,

      "tiktok_feature_enabled": tiktok_feature_enabled,
      "tiktok_recognize_track_feature_enabled": tiktok_recognize_track_feature_enabled,
      "tiktok_quota": tiktok_quota,

      "twitter_feature_enabled": twitter_feature_enabled,
      "likee_feature_enabled": likee_feature_enabled,
      "tumblr_feature_enabled": tumblr_feature_enabled,
      "pinterest_feature_enabled": pinterest_feature_enabled,
      "facebook_feature_enabled": facebook_feature_enabled,

      "youtube_search_feature_enabled": youtube_search_feature_enabled,
      "youtube_download_feature_enabled": youtube_download_feature_enabled,
      "youtube_recognize_track_feature_enabled": youtube_recognize_track_feature_enabled,
      "youtube_quota": youtube_quota,

      "broadcast_feature_enabled": broadcast_feature_enabled,
      "command_feature_enabled": command_feature_enabled,
      "required_join_feature_enabled": required_join_feature_enabled,
      "advertisement_feature_enabled": advertisement_feature_enabled,
      "referral_feature_enabled": referral_feature_enabled,
      "join_request_feature_enabled": join_request_feature_enabled,

      "web_feature_enabled": web_feature_enabled
    }

    async with acquire_connection() as conn:
      cursor = await conn.execute(instance_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"]

  @staticmethod
  async def enable_feature(instance_id: int, feature: str):
    query = sql.SQL(instance_feature_update_sql).format(sql.Composed([sql.Identifier(str(feature)), sql.SQL("="), sql.Literal(True)]))
    params = {"id": instance_id}
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def disable_feature(instance_id: int, feature: str):
    query = sql.SQL(instance_feature_update_sql).format(sql.Composed([sql.Identifier(str(feature)), sql.SQL("="), sql.Literal(False)]))
    params = {"id": instance_id}
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def exists_by_token(token: str):
    params = {"token": token}

    async with acquire_connection() as conn:
      cursor = await conn.execute(instance_exists_by_token_sql, params)
      record = await cursor.fetchone()
      return bool(record)

  @staticmethod
  async def mark_request_for_today(instance_id: int, user_id: int):
    request_key_name = f"instance:{instance_id}:{datetime.datetime.today().strftime('%Y-%m-%d')}:request"
    unique_request_key_name = f"instance:{instance_id}:{datetime.datetime.today().strftime('%Y-%m-%d')}:request:unique"

    pipeline = await redis.pipeline(transaction=True)

    await pipeline.sadd(request_key_name, str(user_id) + str(int(time.time())))
    await pipeline.expire(request_key_name, 60*60*24*9)

    await pipeline.pfadd(unique_request_key_name, str(user_id))

    await pipeline.execute()

  @staticmethod
  async def get_request_mark_count(instance_id: int, date: datetime.date) -> typing.Tuple[int, int]:
    request_key_name = f"instance:{instance_id}:{date.strftime('%Y-%m-%d')}:request"
    unique_request_key_name = f"instance:{instance_id}:{date.strftime('%Y-%m-%d')}:request:unique"

    request_mark_count = await redis.scard(request_key_name)
    unique_request_mark_count = await redis.pfcount(unique_request_key_name)

    return (request_mark_count, unique_request_mark_count)