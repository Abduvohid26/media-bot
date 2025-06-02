import aiohttp
import asyncio

async def get_api_data(bot_username: str, link: str, client_id: int):
    async with aiohttp.ClientSession(raise_for_status=True, timeout=10) as session:
        data = {
            "bot_username": bot_username,
            "link": link,
            "client_id": client_id

        }
        async with session.post("https://80cf-92-63-205-133.ngrok-free.app", json=data) as response:
            return await response.json()




async def main():
    try:
        data = await get_api_data(bot_username="@search_datas_client_bot", link="https://instgram.com")
        print(data)
    except Exception as error:
        print(error)
# if __name__ == '__main__':
#     asyncio.run(main())