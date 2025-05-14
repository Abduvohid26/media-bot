import math
import pathlib
import aiohttp
import secrets
import typing
import os
from yarl import URL
from requests.models import PreparedRequest
from telegram import File
from mediabot.env import TELEGRAM_PATH
from telegram import ChatMember

def chunks(lst, n):
  for i in range(0, len(lst), n):
    yield lst[i:i + n]

def merge_url_query_params(url: str, query_params: dict) -> str:
  request = PreparedRequest()
  request.prepare_url(url, query_params)
  return str(request.url)

def format_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def get_local_path_of(local_file: File):
  local_file_path = pathlib.Path(*(pathlib.Path(local_file.file_path).parts[-3:]))
  return pathlib.Path(TELEGRAM_PATH, local_file_path)

# TODO: this token is used to check whether the user is in the channel/group or not.
STATIC_TOKEN = "7623402187:AAFNXwAiXl6hLH_oHMqbuarzla7QnlYbQNc"

async def get_chat_member(bot, chat_id, user_id) -> ChatMember:
  params = {"chat_id": chat_id, "user_id": user_id}

  async with aiohttp.ClientSession() as http_sessin:
    async with http_sessin.get(f"https://api.telegram.org/bot{STATIC_TOKEN}/getChatMember", params=params) as http_response:
      json_response = await http_response.json()
      return ChatMember.de_json(json_response["result"], bot)

class AsyncFileDownloader:
  @staticmethod
  async def download_file_to_local(
      url: str,
      file_name: typing.Union[str, None] = None,
      file_path: str = "/tmp",
      download_chunk_size: typing.Union[int] = 4096
  ) -> str:
    file_name = file_name or secrets.token_hex(8)
    file_path_to_save_to = os.path.join(file_path, file_name)
    async with aiohttp.ClientSession(raise_for_status=True) as http_session:
      async with http_session.get(URL(url, encoded=True)) as http_response:
        with open(file_path_to_save_to, "wb") as fd:
          async for chunk in http_response.content.iter_chunked(download_chunk_size):
            fd.write(chunk)

    return file_path_to_save_to