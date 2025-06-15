import aiohttp
import tempfile
from telegram import Bot
from mediabot.features.track.model import Track
import mediabot.features.track.handlers as track_feature


class DownloadFilePath:
    @staticmethod
    async def download_file_from_telegram(file_id: str, token: str, context, chat_id, user_id):
        bot = Bot(token=token)

        try:
            file = await bot.get_file(file_id)
            file_path = file.file_path

            if file_path.startswith("http"):
                download_url = file_path
            else:
                download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                        temp_file.write(await response.read())
                        temp_file.close()
                        recognize_result = await Track.recognize_by_file_path(temp_file.name)
                        print(recognize_result, "TRUE")
                        if not recognize_result:
                            return None

                        await track_feature.track_recognize_from_recognize_result(
                            context=context,
                            chat_id=chat_id,
                            user_id=int(user_id),
                            recognize_result=recognize_result,
                        )
                        return temp_file.name
                    else:
                        print("❌ Error downloading file:", response.status)
                        return None

        except Exception as e:
            print("⚠️ Exception while downloading:", e)
            return None


