import aiohttp
import random
from urllib.parse import urljoin
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis

YOUTUBE_DOWNLOAD_TELEGRAM_MAX_ATTEMPTS = 3

class YouTube:
  @staticmethod
  async def search(search_query: str, offset: int, limit: int):
    try:
      params = {"query": search_query, "offset": offset, "limit": limit}

      async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(12), raise_for_status=True) as http_session:
        async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/youtube-search"), params=params) as http_response:
          search_result = await http_response.json()
          print(search_result, "SRES")
          return search_result["search_results"]
    except Exception as ex:
      print(ex, "xatolik")

  @staticmethod
  async def download_telegram(id: str, telegram_bot_token: str, recognize: bool = False, attempt: int = 1) -> str:
    params = {"id": id, "telegram_bot_token": telegram_bot_token}
    if recognize:
      params["recognize"] = 1

    try:
      async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(128), raise_for_status=True) as http_session:
        async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/youtube-download-telegram"), params=params) as http_response:
          json_response = await http_response.json()
          print(MEDIA_SERVICE_BASE_URL, "/youtube-download-telegram", params)
          print(json_response, "JSON RESPONSE")
          return (json_response["file_id"], json_response["recognize_result"],)
    except:
      if attempt <= YOUTUBE_DOWNLOAD_TELEGRAM_MAX_ATTEMPTS:
        return await YouTube.download_telegram(id, telegram_bot_token, recognize, attempt + 1)
      raise Exception("Max attempts reached")

  @staticmethod
  async def set_youtube_cache_file_id(instance_id: int, id: str, audio: bool, file_id: str):
    await redis.set(f"youtube:file_id:{'audio' if audio else 'video'}:{instance_id}:{id}", file_id)

  @staticmethod
  async def get_youtube_cache_file_id(instance_id: int, id: str, audio: bool):
    return await redis.get(f"youtube:file_id:{'audio' if audio else 'video'}:{instance_id}:{id}")
