import aiohttp
import secrets
import json
from mediabot.env import MEDIA_SERVICE_BASE_URL
from mediabot.cache import redis

class MediaService:
  @staticmethod
  async def info(link: str) -> dict:
    params = {"link": link}

    async with aiohttp.ClientSession(MEDIA_SERVICE_BASE_URL, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
      async with http_session.get("/info", params=params) as http_response:
        json_content = await http_response.json()
        return json_content["info"]

  @staticmethod
  async def save_link_info(content: dict):
    content_id = secrets.token_hex(4)
    await redis.set(f"link:info:{content_id}", json.dumps(content), ex=60*60*24)
    return content_id

  @staticmethod
  async def get_link_info(id: str):
    link_content = await redis.get(f"link:info:{id}")
    return json.loads(link_content) if link_content else None