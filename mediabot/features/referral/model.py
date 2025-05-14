import typing
from mediabot.database.connection import acquire_connection

referral_insert_sql = open("mediabot/database/queries/referral-insert.sql").read()
referral_by_code_sql = open("mediabot/database/queries/referral-by-code.sql").read()
referral_click_insert_sql = open("mediabot/database/queries/referral-click-insert.sql").read()
referral_all_sql = open("mediabot/database/queries/referral-all.sql").read()
referral_detailed_sql = open("mediabot/database/queries/referral-detailed.sql").read()
referral_delete_sql = open("mediabot/database/queries/referral-delete.sql").read()
referral_update_code_sql = open("mediabot/database/queries/referral-update-code.sql").read()
referral_count_sql = open("mediabot/database/queries/referral-count.sql").read()

CREATE_REFERRAL_STATE_ENTER = object()
EDIT_REFERRAL_STATE_ENTER = object()

CP_REFERRAL_CURRENT_PAGE_CONTEXT = object()
CP_REFERRAL_PER_PAGE_LIMIT = 10

class _Referral:
  id: int
  code: str
  click_count: int
  created_at: str

class _ReferralDetailedLanguageStatistics:
  language_name: str
  account_count: int

class _ReferralDetailed:
  id: int
  code: str
  account_click_statistics: list[_ReferralDetailedLanguageStatistics]
  account_new_statistics: list[_ReferralDetailedLanguageStatistics]
  created_at: str

class Referral:
  @staticmethod
  def deserialize(record: dict) -> _Referral:
    referral = _Referral()

    referral.id = record["id"]
    referral.code = record["code"]
    referral.click_count = record["click_count"]
    referral.created_at = record["created_at"]

    return referral

  @staticmethod
  def deserialize_detailed(records: list[dict]) -> _ReferralDetailed:
    referral = _ReferralDetailed()

    referral.id = records[0]["referral_id"]
    referral.code = records[0]["referral_code"]
    referral.created_at = records[0]["referral_created_at"]

    referral.account_new_statistics = []
    referral.account_click_statistics = []

    for record in records:
      account_new_statistics = _ReferralDetailedLanguageStatistics()
      account_new_statistics.language_name = record["account_new_language_name"] or "Unknown"
      account_new_statistics.account_count = record["account_new_count"]
      referral.account_new_statistics.append(account_new_statistics)

    for record in records:
      account_click_statistics = _ReferralDetailedLanguageStatistics()
      account_click_statistics.language_name = record["account_click_language_name"] or "Unknown"
      account_click_statistics.account_count = record["account_click_count"]
      referral.account_click_statistics.append(account_click_statistics)

    return referral

  @staticmethod
  async def create(instance_origin: int, code: str) -> None:
    params = {"instance_origin": instance_origin, "code": code}
    async with acquire_connection() as conn:
      await conn.execute(referral_insert_sql, params)

  @staticmethod
  async def get_by_code(instance_origin: int, code: str) -> typing.Union[_Referral, None]:
    params = {"instance_origin": instance_origin, "code": code}
    async with acquire_connection() as conn:
      cursor = await conn.execute(referral_by_code_sql, params)
      record = await cursor.fetchone()
      return Referral.deserialize(record) if record else None

  @staticmethod
  async def create_click(instance_origin: int, referral_origin: int, account_origin: int):
    params = {"instance_origin": instance_origin, "referral_origin": referral_origin, "account_origin": account_origin}

    async with acquire_connection() as conn:
      await conn.execute(referral_click_insert_sql, params)

  @staticmethod
  async def get_all(instance_origin: int, offset: int = 0, limit: int = 10) -> list[_Referral]:
    params = {"instance_origin": instance_origin, "offset": offset, "limit": limit}

    async with acquire_connection() as conn:
      cursor = await conn.execute(referral_all_sql, params)
      records = await cursor.fetchall()
      return [Referral.deserialize(record) for record in records]

  @staticmethod
  async def get_detailed(referral_id: int) -> typing.Union[_ReferralDetailed, None]:
    params = {"referral_id": referral_id}
    async with acquire_connection() as conn:
      cursor = await conn.execute(referral_detailed_sql, params)
      records = await cursor.fetchall()
      return Referral.deserialize_detailed(records)

  @staticmethod
  async def delete(referral_id: int) -> None:
    params = {"referral_id": referral_id}
    async with acquire_connection() as conn:
      await conn.execute(referral_delete_sql, params)

  @staticmethod
  async def update_code(referral_id: int, referral_code: str) -> None:
    params = {"referral_id": referral_id, "referral_code": referral_code}
    async with acquire_connection() as conn:
      await conn.execute(referral_update_code_sql, params)

  @staticmethod
  async def count(instance_origin: int) -> int:
    params = {"instance_origin": instance_origin}
    async with acquire_connection() as conn:
      cursor = await conn.execute(referral_count_sql, params)
      record = await cursor.fetchone()
      return record["count"]
