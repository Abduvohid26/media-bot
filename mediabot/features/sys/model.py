import asyncio
import os
import datetime
import json
from mediabot.database.connection import acquire_connection
from mediabot.env import DATABASE_CONNECTION_URL
from mediabot.cache import redis

sys_database_stat_activity_sql = open("mediabot/database/queries/sys-database-stat-activity.sql").read()

class SysDatabaseStatActivity:
  pid: int
  client_addr: str
  query_start: str
  state: str
  query: str

class Sys:
  @staticmethod
  def deserialize_sys_database_stat_activity(record: dict) -> SysDatabaseStatActivity:
    activity = SysDatabaseStatActivity()

    activity.pid = record["pid"]
    activity.client_addr = record["client_addr"]
    activity.query_start = record["query_start"]
    activity.state = record["state"]
    activity.query = record["query"]

    return activity

  @staticmethod
  async def get_database_stat_activity() -> list[SysDatabaseStatActivity]:
    async with acquire_connection() as conn:
      cursor = await conn.execute(sys_database_stat_activity_sql)
      records = await cursor.fetchall()
      return [Sys.deserialize_sys_database_stat_activity(record) for record in records]

  @staticmethod
  async def backup_accounts() -> str:
    dt = datetime.datetime.now()
    file_name = f"accounts-{dt.strftime('%Y-%m-%d_%H-%M-%S')}.backup"
    file_path = os.path.join("/tmp", file_name)

    command = f"pg_dump {DATABASE_CONNECTION_URL} -t account --data-only --column-inserts --rows-per-insert=1000 -F c > {file_path}"
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    return file_path

  @staticmethod
  async def backup_groups() -> str:
    dt = datetime.datetime.now()
    file_name = f"groups-{dt.strftime('%Y-%m-%d_%H-%M-%S')}.backup"
    file_path = os.path.join("/tmp", file_name)

    command = f"pg_dump {DATABASE_CONNECTION_URL} -t group --data-only --column-inserts --rows-per-insert=1000 -F c > {file_path}"
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    return file_path