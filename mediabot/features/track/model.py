import aiohttp
import random
from urllib.parse import urljoin
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis
from yarl import URL

TRACK_SEARCH_QUERY_CONTEXT = object()
TRACK_DOWNLOAD_TELEGRAM_MAX_ATTEMPTS = 3

class Track:
  @staticmethod
  async def search(query: str, offset: int = 0, limit: int = 10) -> list[dict]:
    params = {"query": query, "offset": offset, "limit": limit}

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5), raise_for_status=True) as http_session:
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
