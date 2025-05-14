import typing
import psycopg.sql as SQL
from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat, BotCommandScopeAllGroupChats
from telegram.ext import ExtBot
from mediabot.database.connection import acquire_connection
from mediabot.features.account.model import ACCOUNT_SYS_ID_LIST, Account

command_by_command_sql = open("mediabot/database/queries/command-by-command.sql").read()
command_insert_sql = open("mediabot/database/queries/command-insert.sql").read()
command_sql = open("mediabot/database/queries/command.sql").read()
command_all_sql = open("mediabot/database/queries/command-all.sql").read()
command_delete_sql = open("mediabot/database/queries/command-delete.sql").read()
command_update_sql = open("mediabot/database/queries/command-update.sql").read()
command_message_all_for_sql = open("mediabot/database/queries/command-message-all-for.sql").read()
command_count_sql = open("mediabot/database/queries/command-count.sql").read()

COMMAND_STATE_NAME = object()

STATIC_COMMANDS = [
  BotCommand("popular_tracks", "Popular tracks by country 🎵🏆"),
  BotCommand("change_language", "Change bot language")
]

GROUP_STATIC_COMMANDS = [
  BotCommand("search", "🎵 Search track")
]

SYS_STATIC_COMMANDS = [
  BotCommand("sys_info", "System Information"),
  BotCommand("sys_db_conn_pool_info", "System Database Connection Pool Information"),
  BotCommand("sys_db_stat_activity_info", "System Database Stat Activity Info"),
  BotCommand("sys_sync_commands", "Synchronize commands"),
  BotCommand("sys_backup", "Backup database (only accounts and groups)"),
  BotCommand("sys_reset_webhook", "Reset webhook"),
  BotCommand("sys_pending_updates", "Pending webhook updates info"),
  BotCommand("sys_reset_pending_updates", "Reset pending updates"),
  BotCommand("sys_features", "Manage features")
]

class _Command:
  id: int
  command: str
  message_count: int
  is_enabled: bool
  language_name: str
  created_at: str

class _CommandMessageFor:
  message: dict
  is_forward: bool

class Command:
  @staticmethod
  def deserialize(record: dict) -> _Command:
    command = _Command()
    command.id = record["command_id"]
    command.command = record["command_command"]
    command.is_enabled = record["command_is_enabled"]
    command.message_count = record["command_message_count"]
    command.created_at = record["command_created_at"]

    return command

  @staticmethod
  def deserialize_message_for(record: dict) -> _CommandMessageFor:
    message = _CommandMessageFor()

    message.message = record["message_message"]
    message.is_forward = record["message_is_forward"]

    return message

  @staticmethod
  async def get_all(instance_origin: int, offset: int = 0, limit: int = 10) -> list[_Command]:
    params = {"instance_origin": instance_origin, "offset": offset, "limit": limit}
    async with acquire_connection() as conn:

      cursor = await conn.execute(command_all_sql, params)
      records = await cursor.fetchall()
      return [Command.deserialize(record) for record in records]

  @staticmethod
  async def get(command_id: int) -> typing.Union[_Command, None]:
    params = {"command_id": command_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(command_sql, params)
      record = await cursor.fetchone()
      return Command.deserialize(record) if record else None

  @staticmethod
  async def get_by_command(instance_origin: int, command: str) -> typing.Union[_Command, None]:
    params = {"instance_origin": instance_origin, "command": command}
    async with acquire_connection() as conn:
      cursor = await conn.execute(command_by_command_sql, params)
      records = await cursor.fetchall()
      return Command.deserialize(records) if records else None
  
  @staticmethod
  async def create(instance_origin: int, command: str) -> int:
    params = {"instance_origin": instance_origin, "command": command}
    async with acquire_connection() as conn:
      cursor = await conn.execute(command_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"]

  @staticmethod
  async def delete(instance_origin: int, command_id: int) -> None:
    params = {"instance_origin": instance_origin, "command_id": command_id}
    async with acquire_connection() as conn:
      await conn.execute(command_delete_sql, params)

  @staticmethod
  async def update(instance_origin: int, command_id: int, fields: dict) -> None:
    update_fields = SQL.SQL(", ").join([
      SQL.Composed([SQL.Identifier(field), SQL.SQL("="), SQL.Literal(fields[field])
    ]) for field in fields.keys()])

    params = {"instance_origin": SQL.Literal(instance_origin), "command_id": SQL.Literal(command_id)}
    query = SQL.SQL(command_update_sql).format(update_fields, **params)
    async with acquire_connection() as conn:
      await conn.execute(query)

  @staticmethod
  async def set_is_enabled(instance_origin: int, command_id: int, is_enabled: bool) -> None:
    await Command.update(instance_origin, command_id, {"is_enabled": is_enabled})

  @staticmethod
  async def get_messages_for(instance_origin: int, account_id: int, command: str) -> list[_CommandMessageFor]:
    params = {"instance_origin": instance_origin, "account_id": account_id, "command": command}
    async with acquire_connection() as conn:
      cursor = await conn.execute(command_message_all_for_sql, params)
      records = await cursor.fetchall()
      return [Command.deserialize_message_for(record) for record in records]

  @staticmethod
  async def sync_commands(instance_origin: int, bot: ExtBot) -> None:
    commands = await Command.get_all(instance_origin)

    # TODO(mhw0): didin't test the code below as telegram clients seems to have command bugs

    private_chat_commands = [BotCommand(command.command.replace("/", ""), "...") for command in commands]

    try:
      await bot.set_my_commands(STATIC_COMMANDS + private_chat_commands, BotCommandScopeAllPrivateChats())
    except: pass

    try:
      await bot.set_my_commands(GROUP_STATIC_COMMANDS, BotCommandScopeAllGroupChats())
    except: pass

    for sys_account_id in ACCOUNT_SYS_ID_LIST:
      try:
        await bot.set_my_commands(STATIC_COMMANDS  + SYS_STATIC_COMMANDS + private_chat_commands, BotCommandScopeChat(sys_account_id))
      except:
        pass

    admin_ids = await Account.get_admin_id_all(instance_origin)
    for admin_id in admin_ids:
      try:
        await bot.set_my_commands(STATIC_COMMANDS  + private_chat_commands, BotCommandScopeChat(admin_id))
      except:
        pass

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(command_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]
