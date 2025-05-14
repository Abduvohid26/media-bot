from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from mediabot.context import Context
from mediabot.features.track.constants import TRACK_SEARCH_LIMIT
from mediabot.utils import chunks

class TrackSearchPaginationKeyboardMarkup:
  @staticmethod
  def build(page: int) -> InlineKeyboardMarkup:
    pagination_buttons = []

    if page != 0:
      pagination_buttons.append(InlineKeyboardButton(f"« {(page*TRACK_SEARCH_LIMIT)-TRACK_SEARCH_LIMIT} - {page*TRACK_SEARCH_LIMIT}", \
          callback_data=f"track_search_previous_{page-1}"))

    pagination_buttons.append(InlineKeyboardButton(f"» {(page*TRACK_SEARCH_LIMIT+TRACK_SEARCH_LIMIT)} - {((page*TRACK_SEARCH_LIMIT)+TRACK_SEARCH_LIMIT*2)}", \
        callback_data=f"track_search_next_{page+1}"))

    return InlineKeyboardMarkup([pagination_buttons])

class TrackSearchDownloadInlineKeyboardMarkup:
  @staticmethod
  def build(tracks: list[dict]) -> InlineKeyboardMarkup:

    inline_buttons = [[InlineKeyboardButton(f"🎵 {row_index*5+col_index+1}",
        callback_data=f"track_download_{track['id']}") for col_index, track in enumerate(row)] \
        for row_index, row in enumerate(chunks(tracks, 5))]

    return InlineKeyboardMarkup(inline_buttons)

class TrackSearchDownloadWebKeyboardMarkup:
  @staticmethod
  def build(tracks: list[dict], context: Context) -> InlineKeyboardMarkup:
    inline_buttons = [[InlineKeyboardButton(f"🎵 {row_index*5+col_index+1}",
        web_app=WebAppInfo("https://exchanger.services/websdk")) for col_index, track in enumerate(row)] \
        for row_index, row in enumerate(chunks(tracks, 5))]

    return InlineKeyboardMarkup(inline_buttons)