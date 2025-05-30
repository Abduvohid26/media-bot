import aiohttp
import random
from urllib.parse import urljoin
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis
from yarl import URL
from typing import List
from datetime import datetime
from mediabot.database.connection import acquire_connection
from dataclasses import dataclass

TRACK_SEARCH_QUERY_CONTEXT = object()
TRACK_DOWNLOAD_TELEGRAM_MAX_ATTEMPTS = 3


track_create_sql = open("mediabot/database/queries/track-create.sql").read()
track_get_sql = open("mediabot/database/queries/track-get.sql").read()
track_search_sql = open("mediabot/database/queries/track-search.sql").read()

@dataclass
class _Track_DB:
    id: int
    query: str
    video_id: str
    title: str
    performer: str
    duration: int
    thumbnail_url: str
    created_at: str


class Track_DB:
    @staticmethod
    def deserialize(record: dict) -> _Track_DB:
        return _Track_DB(
            id=record["id"],
            query=record["query"],
            video_id=record["video_id"],
            title=record["title"],
            performer=record["performer"],
            duration=record["duration"],
            thumbnail_url=record["thumbnail_url"],
            created_at=str(record["created_at"])
        )
    @staticmethod
    async def create(query: str, video_id: str, title: str, performer: str, duration: int, thumbnail_url: str):
        insert_sql = """
        INSERT INTO tracks (query, video_id, title, performer, duration, thumbnail_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        now = datetime.now()

        async with acquire_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    insert_sql,
                    (query, video_id, title, performer, duration, thumbnail_url, now)
                )
                row = await cursor.fetchone()
                return row["id"] if row else None
    @staticmethod
    async def save_all(query: str, search_results: List[dict]):
        insert_sql = """
        INSERT INTO tracks (query, video_id, title, performer, duration, thumbnail_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        now = datetime.now()
        data = [
            (
                query,
                item["id"],
                item["title"],
                item["performer"],
                item["duration"],
                item["thumbnail_url"],
                now
            )
            for item in search_results
        ]

        async with acquire_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.executemany(insert_sql, data)

    @staticmethod
    async def get_by_query(query: str, limit: int = 10) -> List[dict]:
        pattern = f"%{query.strip()}%"
        select_sql = """
            SELECT video_id AS id, title, performer, duration, thumbnail_url
            FROM tracks
            WHERE query ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s;
        """
        async with acquire_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(select_sql, (pattern, limit))
                rows = await cursor.fetchall()
                return rows

    @staticmethod
    async def get(track_id: int) -> _Track_DB | None:
        select_sql = """
        SELECT id, query, video_id, title, performer, duration, thumbnail_url, created_at
        FROM tracks WHERE id = %s;
        """

        async with acquire_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(select_sql, (track_id,))
                record = await cursor.fetchone()
                return Track_DB.deserialize(record) if record else None

    @staticmethod
    async def search(query: str) -> List[_Track_DB]:
        select_sql = """
        SELECT id, query, video_id, title, performer, duration, thumbnail_url, created_at
        FROM tracks
        WHERE query ILIKE %s
        ORDER BY created_at DESC;
        """

        async with acquire_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(select_sql, (f"%{query}%",))
                rows = await cursor.fetchall()
                return [Track_DB.deserialize(row) for row in rows]
            
    @staticmethod
    async def delete_by_video_id(video_id: str):
      delete_sql = """
          DELETE FROM tracks
          WHERE video_id = %s;
      """
      async with acquire_connection() as conn:
          async with conn.cursor() as cursor:
              await cursor.execute(delete_sql, (video_id,))
          await conn.commit()


class Track:
  @staticmethod
  async def search(query: str, offset: int = 0, limit: int = 10) -> list[dict]:
    params = {"query": query, "offset": offset, "limit": limit}

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(15), raise_for_status=True) as http_session:
      async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/track-search"), params=params) as http_response:
        search_result = await http_response.json()
        return search_result["search_results"]

  @staticmethod
  async def download_telegram(track_id: str, telegram_bot_token: str, telegram_bot_username: str, attempt: int = 1) -> str:
    params = {"id": track_id, "telegram_bot_token": telegram_bot_token, "telegram_bot_username": telegram_bot_username}

    try:
      async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(60), raise_for_status=True) as http_session:
        async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, f"/track-download-telegram"), params=params) as http_response:
          json_response = await http_response.json()
          return json_response["file_id"]
    except:
      if attempt <= TRACK_DOWNLOAD_TELEGRAM_MAX_ATTEMPTS:
        return await Track.download_telegram(track_id, telegram_bot_token, telegram_bot_username, attempt + 1)
      raise Exception("Max attempts reached")

  @staticmethod
  async def get_popular_tracks(country_code: str = "US", offset: int = 0, limit: int = 10) -> list[dict]:
    params = {"country_code": country_code, "offset": offset, "limit": limit}

    async with aiohttp.ClientSession() as http_session:
      async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/track-popular"), params=params) as http_response:
        json_response = await http_response.json()
        return json_response["popular_tracks"]

  @staticmethod
  async def set_track_cache_file_id(instance_id: int, track_id: str, file_id: str):
    await redis.set(f"track:file_id:{instance_id}:{track_id}", file_id)

  @staticmethod
  async def get_track_cache_file_id(instance_id: int, track_id: str):
    return await redis.get(f"track:file_id:{instance_id}:{track_id}")

  @staticmethod
  async def recognize_by_file_path(file_path):
    data = {"file": open(file_path, "rb")}

    async with aiohttp.ClientSession() as http_session:
      async with http_session.post(urljoin(MEDIA_SERVICE_BASE_URL, "/track-recognize-by-file"), data=data) as http_response:
        json_response = await http_response.json()
        return json_response["recognize_result"]

  @staticmethod
  async def recognize_by_link(link: str):
    params = {"link": str(URL(link))}

    async with aiohttp.ClientSession(MEDIA_SERVICE_BASE_URL) as http_session:
      async with http_session.post("/track-recognize-by-link", params=params) as http_response:
        json_response = await http_response.json()
        return json_response["recognize_result"]
