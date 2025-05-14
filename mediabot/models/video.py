import aiohttp

class Video:
  @staticmethod
  async def search(query: str, offset: int, limit: int):
    params = {"query": query, "offset": offset, "limit": limit}
    async with aiohttp.ClientSession() as session:
      async with session.get("http://localhost:8007/search", params=params) as resp:
        json_resp = await resp.json()
        return json_resp["search_results"]

  @staticmethod
  async def download(video_id: str) -> str:
    async with aiohttp.ClientSession() as session:
      async with session.get(f"http://localhost:8081/video/{track_id}/download") as resp:
        json_resp = await resp.json()
        return json_resp["file_path"]
