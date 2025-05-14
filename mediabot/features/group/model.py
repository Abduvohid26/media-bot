import datetime
import psycopg.sql as sql

from mediabot.database.connection import acquire_connection

group_try_insert_sql = open("mediabot/database/queries/group-try-insert.sql").read()
group_group_id_many_for_broadcast_sql = open("mediabot/database/queries/group-group-id-many-for-broadcast.sql").read()
group_deleted_at_set_many_sql = open("mediabot/database/queries/group-deleted-at-set-many.sql").read()
group_statistics_sql = open("mediabot/database/queries/group-statistics.sql").read()

class _GroupForBroadcast:
  id: int
  group_id: int

class _GroupStatistics:
  group_count: int
  today_new_group_count: int
  deleted_group_count: int
  today_deleted_group_count: int

class Group:
  @staticmethod
  def deserialize_group_for_broadcast(record: dict) -> _GroupForBroadcast:
    account = _GroupForBroadcast()

    account.id = record["id"]
    account.group_id = record["group_id"]

    return account

  @staticmethod
  def deserialize_statistics(data: dict) -> _GroupStatistics:
    statistics = _GroupStatistics()

    statistics.group_count = data["group_count"]
    statistics.today_new_group_count = data["today_new_group_count"]
    statistics.today_deleted_group_count = data["today_deleted_group_count"]
    statistics.deleted_group_count = data["deleted_group_count"]

    return statistics

  @staticmethod
  async def try_create(instance_origin: int, group_id: int) -> None:
    params = {"instance_origin": instance_origin, "group_id": group_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(group_try_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"] if record else None

  @staticmethod
  async def get_many_for_broadcast(instance_origin: int, cursor: int, limit: int) -> list[_GroupForBroadcast]:
    params = {"instance_origin": instance_origin, "cursor": cursor, "limit": limit}
    async with acquire_connection() as conn:
      cursor = await conn.execute(group_group_id_many_for_broadcast_sql, params)
      records = await cursor.fetchall()
      return [Group.deserialize_group_for_broadcast(record) for record in records]

  @staticmethod
  async def set_deleted_at_many(instance_origin: int, account_id_list: list[int]):
    account_id_sql = sql.SQL(", ").join([sql.Literal(account_id) for account_id in account_id_list])
    query = sql.SQL(group_deleted_at_set_many_sql).format(account_id_sql)
    params = {"instance_origin": instance_origin, "deleted_at": datetime.datetime.now()}

    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def get_statistics(instance_origin: int) -> _GroupStatistics:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(group_statistics_sql, params)
      record = await cursor.fetchone()
      return Group.deserialize_statistics(record)
