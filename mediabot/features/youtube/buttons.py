from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from mediabot.context import Context
from mediabot.features.youtube.constants import YOUTUBE_SEARCH_LIMIT
from mediabot.utils import chunks

class YouTubeSearchPaginationKeyboardMarkup:
  @staticmethod
  def build(page: int) -> InlineKeyboardMarkup:
    pagination_buttons = []

    if page != 0:
      pagination_buttons.append(InlineKeyboardButton(f"« {(page*YOUTUBE_SEARCH_LIMIT)-YOUTUBE_SEARCH_LIMIT} - {page*YOUTUBE_SEARCH_LIMIT}", \
          callback_data=f"youtube_search_previous_{page-1}"))

    pagination_buttons.append(InlineKeyboardButton(f"» {(page*YOUTUBE_SEARCH_LIMIT+YOUTUBE_SEARCH_LIMIT)} - {((page*YOUTUBE_SEARCH_LIMIT)+YOUTUBE_SEARCH_LIMIT*2)}", \
        callback_data=f"youtube_search_next_{page+1}"))

    return InlineKeyboardMarkup([pagination_buttons])

class YouTubeSearchDownloadInlineKeyboardMarkup:
  @staticmethod
  def build(videos: list[dict]) -> InlineKeyboardMarkup:

    inline_buttons = [[InlineKeyboardButton(f"🎞 {row_index*5+col_index+1}",
        callback_data=f"youtube_preview_{video['id']}") for col_index, video in enumerate(row)] \
        for row_index, row in enumerate(chunks(videos, 5))]

    return InlineKeyboardMarkup(inline_buttons)

class YouTubeSearchDownloadWebKeyboardMarkup:
  @staticmethod
  def build(tracks: list[dict], context: Context) -> InlineKeyboardMarkup:
    inline_buttons = [[InlineKeyboardButton(f"🎵 {row_index*5+col_index+1}",
        web_app=WebAppInfo("https://exchanger.services/websdk")) for col_index, track in enumerate(row)] \
        for row_index, row in enumerate(chunks(tracks, 5))]

    return InlineKeyboardMarkup(inline_buttons)