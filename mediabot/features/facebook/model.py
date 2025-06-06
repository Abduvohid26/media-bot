import aiohttp
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis
from urllib.parse import urljoin

class Facebook:
  @staticmethod
  async def download_telegram(link: str, telegram_bot_token: str) -> dict:
    params = {"link": link, "telegram_bot_token": telegram_bot_token}
    async with aiohttp.ClientSession(MEDIA_SERVICE_BASE_URL, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
      async with http_session.get("/facebook-download-telegram", params=params) as http_response:
        json_response = await http_response.json()
        return json_response["file_id"]
      
  @staticmethod
  async def get(link: str) -> dict:
    params = {"link": link}

    async with aiohttp.ClientSession(raise_for_status=True, timeout=aiohttp.ClientTimeout(32)) as http_session:
      async with http_session.get(urljoin(MEDIA_SERVICE_BASE_URL, "/facebook-link"), params=params) as http_response:
        return await http_response.json()

  @staticmethod
  async def set_facebook_cache_file_id(instance_id: int, link: str, file_id: str):
    await redis.set(f"facebook:file_id:{instance_id}:{link}", file_id)

  @staticmethod
  async def get_facebook_cache_file_id(instance_id: int, link: str):
    return await redis.get(f"facebook:file_id:{instance_id}:{link}")