# from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler

# from mediabot.features.tiktok.handlers import tiktok_handle_download_callback_query, tiktok_handle_link_message

# class TikTokFeature:
#   tiktok_link_message_handler = MessageHandler(filters.Regex(r"https?:\/\/(?:m|www|vm|vt)\.tiktok\.com\/\S*?\b(?:(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+)|(?=\w{7})(\w*?[A-Z\d]\w*)(?=\s|\/$))") & filters.ChatType.PRIVATE, tiktok_handle_link_message)
#   tiktok_download_callback_query_handler = CallbackQueryHandler(tiktok_handle_download_callback_query, "^tiktok_download_([0-9]+)_(.+)$")

#   @staticmethod
#   def register_handlers(botapp: Application):
#     botapp.add_handler(TikTokFeature.tiktok_link_message_handler)
#     botapp.add_handler(TikTokFeature.tiktok_download_callback_query_handler)


from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler

from mediabot.features.tiktok.handlers import tiktok_handle_download_callback_query, tiktok_handle_link_message

class TikTokFeature:
  tiktok_link_message_handler = MessageHandler(
      filters.Regex(r"https?://(?:m|www|vm|vt)\.tiktok\.com/[^\s]+") & filters.ChatType.PRIVATE, 
      tiktok_handle_link_message
  )
  
  tiktok_download_callback_query_handler = CallbackQueryHandler(
      tiktok_handle_download_callback_query, "^tiktok_download_([0-9]+)_(.+)$"
  )

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TikTokFeature.tiktok_link_message_handler)
    botapp.add_handler(TikTokFeature.tiktok_download_callback_query_handler)
