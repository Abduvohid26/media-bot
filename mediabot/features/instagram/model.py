import aiohttp
from urllib.parse import urljoin
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis

class Instagram:
  @staticmethod
  async def get(link: str) -> dict:
    params = {"link": link}

    async with aiohttp.ClientSession(raise_for_status=True, timeout=aiohttp.ClientTimeout(32)) as http_session:
      async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/instagram-link"), params=params) as http_response:
        return await http_response.json()

  @staticmethod
  async def download_telegram(link: str, telegram_bot_token: str, index=None) -> dict:
    params = {"link": link, "telegram_bot_token": telegram_bot_token}

    if index: params["index"] = index

    async with aiohttp.ClientSession(raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
      async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/instagram-download-telegram"), params=params) as http_response:
        json_response = await http_response.json()
        return json_response["file_id"]

  @staticmethod
  async def set_instagram_cache_file_id(instance_id: int, id: str, file_id: str):
    await redis.set(f"instagram:file_id:{instance_id}:{id}", file_id)

  @staticmethod
  async def get_instagram_cache_file_id(instance_id: int, id: str):
    return await redis.get(f"instagram:file_id:{instance_id}:{id}")