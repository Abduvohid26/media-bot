from telegram.ext import filters, MessageHandler, CallbackQueryHandler
from mediabot.application import Application
from mediabot.features.youtube.handlers import youtube_handle_link_message, youtube_handle_preview_callback_query, \
    youtube_handle_search_message, youtube_handle_video_download_callback_query

class YouTubeSearchFeature:
  youtube_search_message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, youtube_handle_search_message)
  youtube_preview_callback_query_handler = CallbackQueryHandler(youtube_handle_preview_callback_query, "^youtube_preview_([:a-zA-Z0-9_-]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(YouTubeSearchFeature.youtube_search_message_handler)
    botapp.add_handler(YouTubeSearchFeature.youtube_preview_callback_query_handler)

YOUTUBE_LINK_FEATURE_HANDLERS_REGISTERED_CONTEXT = object()

class YouTubeDownloadFeature:
  youtube_video_callback_query_handler = CallbackQueryHandler(youtube_handle_video_download_callback_query, "^youtube_video_download_([:a-zA-Z0-9_-]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    if YOUTUBE_LINK_FEATURE_HANDLERS_REGISTERED_CONTEXT in botapp.bot_data:
      return

    botapp.add_handler(YouTubeDownloadFeature.youtube_video_callback_query_handler)

    botapp.bot_data.setdefault(YOUTUBE_LINK_FEATURE_HANDLERS_REGISTERED_CONTEXT)

class YouTubeLinkFeature:
  youtube_link_message_handler = MessageHandler(filters.Regex("((youtu.*be.*)/(watch?v=|embed/|v|shorts|)(.*?((?=[&#  ?])|$)))"), youtube_handle_link_message)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(YouTubeLinkFeature.youtube_link_message_handler)
