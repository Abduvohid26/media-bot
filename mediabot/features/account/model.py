import typing
import datetime
import psycopg.sql as sql

from mediabot.database.connection import acquire_connection

account_sql = open("mediabot/database/queries/account.sql").read()
account_insert_sql = open("mediabot/database/queries/account-insert.sql").read()
account_set_language_from_language_code_sql = open("mediabot/database/queries/account-set-language-from-language-code.sql").read()
account_set_referral_origin_sql = open("mediabot/database/queries/account-set-referral-origin.sql").read()
account_is_admin_all_sql = open("mediabot/database/queries/account-is-admin-all.sql").read()
account_update_language_origin_sql = open("mediabot/database/queries/account-update-language-origin.sql").read()
account_update_is_admin_sql = open("mediabot/database/queries/account-update-is-admin.sql").read()
account_telegram_id_many_for_broadcast_sql = open("mediabot/database/queries/account-telegram-id-many-for-broadcast.sql").read()
account_statistics_pql = open("mediabot/database/queries/account-statistics.sql").read()
account_deleted_at_set_many_sql = open("mediabot/database/queries/account-deleted-at-set-many.sql").read()
account_deleted_at_set_sql = open("mediabot/database/queries/account-deleted-at-set.sql").read()
account_deleted_at_unset_sql = open("mediabot/database/queries/account-deleted-at-unset.sql").read()

ACCOUNT_ID_CONTEXT = object()
ACCOUNT_REQUEST_RATE_LIMITER_CONTEXT = object()
ACCOUNT_SYS_ID_LIST = [5700964012, 343103355]

class _AccountForBroadcast:
  id: int
  telegram_id: int

class _AccountStatistics:
  language_name: typing.Union[str, None]
  account_count: int
  today_new_account_count: int
  deleted_account_count: int
  today_deleted_account_count: int

class _AccountReferral:
  id: int
  code: str
  click_count: int
  created_at: str

class _AccountLanguage:
  id: int
  code: str
  name: str

class _Account:
  id: int
  telegram_id: int
  language: typing.Union[_AccountLanguage, None]
  referral: typing.Union[_AccountReferral, None]
  is_admin: bool
  created_at: int

class Account:
  @staticmethod
  def deserialize(record: dict) -> _Account:
    account = _Account()
    account_language = None
    account_referral = None

    if record["language_id"]:
      account_language = _AccountLanguage()
      account_language.id = record["language_id"]
      account_language.code = record["language_code"]
      account_language.name = record["language_name"]

    if record["referral_id"]:
      account_referral = _AccountReferral()
      account_referral.id = record["referral_id"]
      account_referral.code = record["referral_code"]
      account_referral.created_at = record["referral_created_at"]

    account.id = record["id"]
    account.telegram_id = record["telegram_id"]
    account.language = account_language
    account.referral = account_referral
    account.is_admin = record["is_admin"]
    account.created_at = record["created_at"]
    return account

  @staticmethod
  def deserialize_statistics(record: dict) -> _AccountStatistics:
    statistics = _AccountStatistics()

    statistics.language_name = record["language_name"]
    statistics.account_count = record["account_count"]
    statistics.today_new_account_count = record["today_new_account_count"]
    statistics.deleted_account_count = record["deleted_account_count"]
    statistics.today_deleted_account_count = record["today_deleted_account_count"]

    return statistics

  @staticmethod
  def deserialize_account_for_broadcast(record: dict) -> _AccountForBroadcast:
    account = _AccountForBroadcast()

    account.id = record["id"]
    account.telegram_id = record["telegram_id"]

    return account

  @staticmethod
  async def try_create(instance_origin: int, account_telegram_id: int, language_code: typing.Union[str, None],
      referral_code: typing.Optional[str] = None) -> typing.Union[int, None]:
    params = {
      "telegram_id": account_telegram_id,
      "instance_origin": instance_origin,
      "language_code": language_code,
      "referral_code": referral_code
    }
    async with acquire_connection() as conn:
      cursor = await conn.execute(account_insert_sql, params)
      record = await cursor.fetchone()
      return record["id"] if record else None

  @staticmethod
  async def get(instance_origin: int, account_telegram_id: int) -> typing.Union[_Account, None]:
    params = {"instance_origin": instance_origin, "account_telegram_id": account_telegram_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(account_sql, params)
      record = await cursor.fetchone()
      return Account.deserialize(record) if record else None

  @staticmethod
  async def set_referral_origin(instance_origin: int, account_id: int, referral_origin: int) -> None:
    params = {"instance_origin": instance_origin, "referral_origin": referral_origin, "account_id": account_id}
    async with acquire_connection() as conn:
      await conn.execute(account_set_referral_origin_sql, params)

  @staticmethod
  async def set_language_origin(account_id: int, language_origin: int) -> None:
    params = {"account_id": account_id, "language_origin": language_origin}
    async with acquire_connection() as conn:
      await conn.execute(account_update_language_origin_sql, params)

  @staticmethod
  async def set_is_admin(instance_origin: int, telegram_id: int, is_admin: bool) -> None:
    params = {"instance_origin": instance_origin, "telegram_id": telegram_id, "is_admin": is_admin}
    async with acquire_connection() as conn:
      await conn.execute(account_update_is_admin_sql, params)

  @staticmethod
  async def get_admin_id_all(instance_origin: int) -> list[int]:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(account_is_admin_all_sql, params)
      records = await cursor.fetchall()

      return [record["telegram_id"] for record in records]

  @staticmethod
  async def get_many_for_broadcast(instance_origin: int, cursor: int, language_origin: int, limit: int) -> list[_AccountForBroadcast]:
    params = {"instance_origin": instance_origin, "cursor": cursor, "language_origin": language_origin, "limit": limit}
    async with acquire_connection() as conn:
      cursor = await conn.execute(account_telegram_id_many_for_broadcast_sql, params)
      records = await cursor.fetchall()
      return [Account.deserialize_account_for_broadcast(record) for record in records]

  @staticmethod
  async def get_statistics(instance_origin: int) -> list[_AccountStatistics]:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(account_statistics_pql, params)
      records = await cursor.fetchall()
      deserialized_data = [Account.deserialize_statistics(record) for record in records]
      deserialized_data.sort(key=(lambda statistics: statistics.language_name is None))
      return deserialized_data

  @staticmethod
  async def set_deleted_at_many(instance_origin: int, account_id_list: list[int]):
    account_id_sql = sql.SQL(", ").join([sql.Literal(account_id) for account_id in account_id_list])
    query = sql.SQL(account_deleted_at_set_many_sql).format(account_id_sql)
    params = {"instance_origin": instance_origin, "deleted_at": datetime.datetime.now()}

    async with acquire_connection() as conn:
      await conn.execute(query, params)

  @staticmethod
  async def set_deleted_at(account_id: int):
    params = {"account_id": account_id}

    async with acquire_connection() as conn:
      await conn.execute(account_deleted_at_set_sql, params)

  @staticmethod
  async def unset_deleted_at(account_id: int):
    params = {"account_id": account_id}

    async with acquire_connection() as conn:
      await conn.execute(account_deleted_at_unset_sql, params)

def deserialize_account(record: dict) -> _Account:
  account = _Account()
  account_language = None
  account_referral = None

  if record["language_id"]:
    account_language = _AccountLanguage()
    account_language.id = record["language_id"]
    account_language.code = record["language_code"]
    account_language.name = record["language_name"]

  if record["referral_id"]:
    account_referral = _AccountReferral()
    account_referral.id = record["referral_id"]
    account_referral.code = record["referral_code"]
    account_referral.created_at = record["referral_created_at"]

  account.id = record["id"]
  account.language = account_language if account_language else None
  account.referral = account_referral if account_referral else None
  account.created_at = record["created_at"]
  return account


async def account_get(instance_origin: int, account_id: int) -> typing.Union[_Account, None]:
  params = {"instance_origin": instance_origin, "account_id": account_id}
  async with acquire_connection() as conn:
    cursor = await conn.execute(account_sql, params)
    record = await cursor.fetchone()
    return deserialize_account(record) if record else None


async def account_try_create(instance_origin: int, account_id: int, language_code: typing.Union[str, None]) -> typing.Union[int, None]:
  params = {"account_id": account_id,
            "instance_origin": instance_origin, "language_code": language_code}
  async with acquire_connection() as conn:
    cursor = await conn.execute(account_insert_sql, params)
    record = await cursor.fetchone()
    return record["id"] if record else None


async def account_set_language_from_language_code(instance_origin: int, account_id: int, language_code: str) -> None:
  params = {"instance_origin": instance_origin,
            "account_id": account_id, "language_code": language_code}
  async with acquire_connection() as conn:
    await conn.execute(account_set_language_from_language_code_sql, params)
