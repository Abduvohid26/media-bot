from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from mediabot.utils import chunks

class MediaDownloaderCollectionKeyboardMarkup:
  @staticmethod
  def build(items: list[dict], link_content_id: str) -> InlineKeyboardMarkup:
    collection_buttons = [[InlineKeyboardButton(f"{'🖼' if post['type'] == 'photo' else '🎞'}",
        callback_data=f"media_download_{link_content_id}_{col_index+row_index}") for col_index, post in enumerate(row)] \
        for row_index, row in enumerate(chunks(items, 5))]

    return InlineKeyboardMarkup(collection_buttons)