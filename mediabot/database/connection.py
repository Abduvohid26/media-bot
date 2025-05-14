from typing import Dict, Union, AsyncContextManager
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from psycopg import AsyncConnection
from mediabot.env import DATABASE_CONNECTION_URL, DATABASE_CONNECTION_POOL_MIN_SIZE, DATABASE_CONNECTION_POOL_MAX_SIZE

CONNECTION_POOL: Union[AsyncConnectionPool, None] = None

def acquire_connection(timeout: int = 30) -> AsyncContextManager[AsyncConnection]:
  global CONNECTION_POOL

  if not CONNECTION_POOL:
    CONNECTION_POOL = AsyncConnectionPool(DATABASE_CONNECTION_URL, min_size=DATABASE_CONNECTION_POOL_MIN_SIZE, \
        max_size=DATABASE_CONNECTION_POOL_MAX_SIZE, kwargs={"row_factory": dict_row}, check=AsyncConnectionPool.check_connection)

  return CONNECTION_POOL.connection(timeout)

async def close_pool() -> None:
  if not CONNECTION_POOL:
    return

  await CONNECTION_POOL.close()

def get_pool_stats() -> Dict[str, int]:
  if not CONNECTION_POOL:
    return {}

  return CONNECTION_POOL.get_stats()
