from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler
from mediabot.features.media_downloader.handlers import media_downloader_handle_link_message, media_downloader_handle_download_callback_query

class TwitterFeature:
  twitter_link_message_handler = MessageHandler(filters.Regex(r"https?://(?:www\.)?(?:x\.com|twitter\.com)/[^/]+/status/\d+") & filters.ChatType.PRIVATE, media_downloader_handle_link_message)
  twitter_download_callback_query_handler = CallbackQueryHandler(media_downloader_handle_download_callback_query, "^media_download_([a-zA-Z0-9]+)_([0-9]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TwitterFeature.twitter_link_message_handler)
    botapp.add_handler(TwitterFeature.twitter_download_callback_query_handler)