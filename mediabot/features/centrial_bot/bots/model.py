
import aiohttp
from mediabot.env import CENTRAL_BOT_API



class CentralBot:
    @staticmethod
    async def check_main_bot(link: str, bot_token: str, bot_username: str, client_id: int):
        data = {"external_link": link, "external_bot_token": bot_token, "external_bot_username": bot_username, "external_clent_id": client_id}
        try:
            async with aiohttp.ClientSession(base_url=CENTRAL_BOT_API, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
                async with http_session.post("/api/check-media", json=data) as http_response:
                    return await http_response.json()
        except Exception as e:
            print("ERROR IN CENTRAL BOT ON (check_main_bot)", str(e))


    async def api_send_external_media(link: str, bot_token: str, bot_username: str, client_id: int, channel_id: str, message_id: int):
        data = {"external_link": link, "external_bot_token": bot_token, "external_bot_username": bot_username, "external_clent_id": client_id, "external_channle_id": channel_id, "external_message_id": message_id}
        try:
            async with aiohttp.ClientSession(base_url=CENTRAL_BOT_API, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
                async with http_session.post("/api/send-external-media", json=data) as http_response:
                    return await http_response.json()
        except Exception as e:
            print("ERROR IN CENTRAL BOT ON (check_main_bot)", str(e))


    async def get_channel_id():
        try:
            async with aiohttp.ClientSession(base_url=CENTRAL_BOT_API, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
                async with http_session.get("/api/random-channel") as http_response:
                    return await http_response.json()
        except Exception as e:
            print("ERROR IN CENTRAL BOT ON (get_channel_id)", str(e))


    async def get_user_bot():
        try:
            async with aiohttp.ClientSession(base_url=CENTRAL_BOT_API, raise_for_status=True, timeout=aiohttp.ClientTimeout(64)) as http_session:
                async with http_session.get("/api/random-userbot") as http_response:
                    return await http_response.json()
        except Exception as e:
            print("ERROR IN CENTRAL BOT ON (get_user_bot)", str(e))