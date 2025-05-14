from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler
from mediabot.features.media_downloader.handlers import media_downloader_handle_link_message, media_downloader_handle_download_callback_query

class LikeeFeature:
  likee_link_message_handler = MessageHandler(filters.Regex(r"https?://(?:l\.likee\.video|likee\.video|likee\.com)/(@[\w.]+/video/|v/)([\w\d]+)") & filters.ChatType.PRIVATE, media_downloader_handle_link_message)
  likee_download_callback_query_handler = CallbackQueryHandler(media_downloader_handle_download_callback_query, "^media_download_([a-zA-Z0-9]+)_([0-9]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(LikeeFeature.likee_link_message_handler)
    botapp.add_handler(LikeeFeature.likee_download_callback_query_handler)