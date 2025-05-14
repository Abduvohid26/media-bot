import re
from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler
from mediabot.features.media_downloader.handlers import media_downloader_handle_link_message, media_downloader_handle_download_callback_query

class TumblrFeature:
  tumblr_link_regex = re.compile(
    r'https?://(?:64\.media|media|va\.media)\.tumblr\.com/[\w/.-]+/tumblr_[\w\d]+(?:\.\w+)?'
    r'|https?://www\.tumblr\.com(?:/@[\w-]+|/communities/[\w-]+)?/post/\d+(?:/[\w-]+)*'
  )
  tumblr_link_message_handler = MessageHandler(filters.Regex(tumblr_link_regex) & filters.ChatType.PRIVATE, media_downloader_handle_link_message)
  tumblr_download_callback_query_handler = CallbackQueryHandler(media_downloader_handle_download_callback_query, "^media_download_([a-zA-Z0-9]+)_([0-9]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TumblrFeature.tumblr_link_message_handler)
    botapp.add_handler(TumblrFeature.tumblr_download_callback_query_handler)