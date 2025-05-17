import aiohttp
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis

class TikTok:
  @staticmethod
  async def download_telegram(link: str, telegram_bot_token: str) -> dict:
    params = {"link": link, "telegram_bot_token": telegram_bot_token}
    print("salom")
    async with aiohttp.ClientSession(MEDIA_SERVICE_BASE_URL, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
      async with http_session.get("/tiktok-download-telegram", params=params) as http_response:
        print("Para")
        json_response = await http_response.json()
        return json_response["file_id"]

  @staticmethod
  async def set_tiktok_cache_file_id(instance_id: int, link: str, file_id: str):
    await redis.set(f"tiktok:file_id:{instance_id}:{link}", file_id)

  @staticmethod
  async def get_tiktok_cache_file_id(instance_id: int, link: str):
    return await redis.get(f"tiktok:file_id:{instance_id}:{link}")