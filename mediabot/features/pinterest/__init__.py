from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler
from mediabot.features.media_downloader.handlers import media_downloader_handle_link_message, media_downloader_handle_download_callback_query

class PinterestFeature:
  pinterest_link_message_handler = MessageHandler(filters.Regex(r"https://(www\.)?pinterest\.(com|ca|co\.uk|fr)/pin/[\w-]+/") & filters.ChatType.PRIVATE, media_downloader_handle_link_message)
  pinterest_download_callback_query_handler = CallbackQueryHandler(media_downloader_handle_download_callback_query, "^media_download_([a-zA-Z0-9]+)_([0-9]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(PinterestFeature.pinterest_link_message_handler)
    botapp.add_handler(PinterestFeature.pinterest_download_callback_query_handler)