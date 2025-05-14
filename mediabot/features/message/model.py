import typing
import psycopg.sql as sql

from telegram import Message as TelegramMessage
from telegram.ext import ExtBot
from mediabot.database.connection import acquire_connection
from mediabot.features.message.constants import MESSAGE_KIND_ADVERTISEMENT, MESSAGE_KIND_JOIN_REQUEST, MESSAGE_KIND_REQUIRED_JOIN,MESSAGE_KIND_COMMAND

message_all_sql = open("mediabot/database/queries/message-all.sql").read()
message_update_sql = open("mediabot/database/queries/message-update.sql").read()
message_sql = open("mediabot/database/queries/message.sql").read()
message_delete_sql = open("mediabot/database/queries/message-delete.sql").read()
message_insert_sql = open("mediabot/database/queries/message-insert.sql").read()
message_seen_insert_sql = open("mediabot/database/queries/message-seen-insert.sql").read()

CP_MESSAGE_KIND_CONTEXT = object()
CP_MESSAGE_ORIGIN_CONTEXT = object()
CP_MESSAGE_CURRENT_PAGE_CONTEXT = object()
CP_MESSAGE_MESSAGE_EDIT_CONTEXT = object()
CP_MESSAGE_LANGUAGE_EDIT_CONTEXT = object()
CP_MESSAGE_PER_PAGE_LIMIT = 10

MESSAGE_STATE_MESSAGE_EDIT = object()
MESSAGE_STATE_LANGUAGE_EDIT = object()
MESSAGE_STATE_MESSAGE_ADD = object()

class _MessageLanguage:
  id: int
  name: str
  code: str

class _Message:
  id: int
  message: dict
  language: typing.Union[_MessageLanguage, None]
  is_attach: bool
  is_forward: bool
  is_after_join: bool
  created_at: str

class Message:
  @staticmethod
  def deserialize(record: dict) -> _Message:
    message = _Message()
    language = None

    message.id = record["message_id"]
    message.message = record["message_message"]
    message.is_attach = record["message_is_attach"]
    message.is_forward = record["message_is_forward"]
    message.is_after_join = record["message_is_after_join"]
    message.created_at = record["message_created_at"]

    if record["message_language_id"]:
      language = _MessageLanguage()
      language.id = record["message_language_id"]
      language.code = record["message_language_code"]
      language.name = record["message_language_name"]

    message.language = language

    return message

  @staticmethod
  def get_type_from(message: dict) -> str:
    if "text" in message and message["text"]:
      return "📝 Text"
    elif "audio" in message and message["audio"]:
      return "🎧 Audio"
    elif "voice" in message and message["voice"]:
      return "🎤 Voice"
    elif "photo" in message and message["photo"]:
      return "🖼 Photo"
    elif "video" in message and message["video"]:
      return "🎞 Video"
    elif "video_note" in message and message["video_note"]:
      return "🔘 Video note"
    elif "document" in message and message["document"]:
      return "📄 Document"

    return "-"

  @staticmethod
  def get_preview_from(message: dict, width = 50) -> str:
    if "text" in message and message["text"]:
      return message["text"][:width] + "..." if len(message["text"]) > width else message["text"]

    return "-"

  @staticmethod
  async def get(message_id: int) -> typing.Union[_Message, None]:
    params = {"message_id": message_id}

    async with acquire_connection() as conn:
      cursor = await conn.execute(message_sql, params)
      record = await cursor.fetchone()

      return Message.deserialize(record) if record else None

  @staticmethod
  async def get_messages(kind: int, origin: int, offset: int = 0, limit: int = 0):
    params = {
      "command_origin": None,
      "required_join_origin": None,
      "join_request_chat_origin": None,
      "advertisement_origin": None,
      "offset": offset,
      "limit": limit
    }

    if kind == MESSAGE_KIND_COMMAND:
      params["command_origin"] = origin
    elif kind == MESSAGE_KIND_REQUIRED_JOIN:
      params["required_join_origin"] = origin
    elif kind == MESSAGE_KIND_JOIN_REQUEST:
      params["join_request_chat_origin"] = origin
    elif kind == MESSAGE_KIND_ADVERTISEMENT:
      params["advertisement_origin"] = origin

    async with acquire_connection() as conn:
      cursor = await conn.execute(message_all_sql, params)
      records = await cursor.fetchall()

      return [Message.deserialize(record) for record in records]

  @staticmethod
  async def update(message_id: int, fields: dict) -> None:
    update_fields = sql.SQL(", ").join([
      sql.Composed([sql.SQL(field), sql.SQL("="), sql.Literal(fields[field])])
          for field in fields.keys()
    ])

    params = {"message_id": message_id}
    query = sql.SQL(message_update_sql).format(update_fields)
    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def update_message(message_id: int, message: str) -> None:
    fields = {"message": message}
    await Message.update(message_id, fields)

  @staticmethod
  async def update_language_origin(message_id: int, language_origin: int) -> None:
    fields = {"language_origin": language_origin}
    await Message.update(message_id, fields)

  @staticmethod
  async def update_is_attach(message_id: int, is_attach: bool) -> None:
    fields = {"is_attach": is_attach}
    await Message.update(message_id, fields)

  @staticmethod
  async def update_is_forward(message_id: int, is_forward: bool) -> None:
    fields = {"is_forward": is_forward}
    await Message.update(message_id, fields)

  @staticmethod
  async def update_is_after_join(message_id: int, is_after_join: bool) -> None:
    fields = {"is_after_join": is_after_join}
    await Message.update(message_id, fields)

  @staticmethod
  async def delete(message_id: int) -> None:
    params = {"message_id": message_id}
    async with acquire_connection() as conn:
      await conn.execute(message_delete_sql, params)

  @staticmethod
  async def create(instance_origin: int, kind: int, origin: int, message: str) -> None:
    params = {
      "instance_origin": instance_origin,
      "command_origin": None,
      "required_join_origin": None,
      "join_request_chat_origin": None,
      "advertisement_origin": None,
      "message": message
    }

    if kind == MESSAGE_KIND_COMMAND:
      params["command_origin"] = origin
    elif kind == MESSAGE_KIND_REQUIRED_JOIN:
      params["required_join_origin"] = origin
    elif kind == MESSAGE_KIND_JOIN_REQUEST:
      params["join_request_chat_origin"] = origin
    elif kind == MESSAGE_KIND_ADVERTISEMENT:
      params["advertisement_origin"] = origin

    async with acquire_connection() as conn:
      await conn.execute(message_insert_sql, params)

  @staticmethod
  async def try_create_message_seen(message_origin: int, account_origin: int, instance_origin: int) -> None:
    params = {"message_origin": message_origin, "account_origin": account_origin, "instance_origin": instance_origin}
    async with acquire_connection() as conn:
      await conn.execute(message_seen_insert_sql, params)

  @staticmethod
  async def send_from_message(chat_id: int, message: TelegramMessage, bot: ExtBot) -> typing.Union[TelegramMessage, None]:
    common_attrs = {"reply_markup": message.reply_markup, "parse_mode": ""}

    if message.text:
      return await bot.send_message(chat_id, message.text, entities=message.entities, **common_attrs)

    common_attrs["caption"] = message.caption

    if message.photo:
      target_photo = max(message.photo, key=lambda x: x.width)
      return await bot.send_photo(chat_id, target_photo.file_id, caption_entities=message.caption_entities, **common_attrs)
    elif message.video:
      return await bot.send_video(chat_id, message.video.file_id, caption_entities=message.caption_entities, **common_attrs)
    elif message.audio:
      return await bot.send_audio(chat_id, message.audio.file_id, caption_entities=message.caption_entities, **common_attrs)
    elif message.voice:
      return await bot.send_voice(chat_id, message.voice.file_id, caption_entities=message.caption_entities, **common_attrs)
    elif message.document:
      return await bot.send_document(chat_id, message.document.file_id, caption_entities=message.caption_entities, **common_attrs)
    elif message.video_note:
      return await bot.send_video_note(chat_id, message.video_note.file_id)

    return None
