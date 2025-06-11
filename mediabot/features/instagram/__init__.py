from telegram.ext import filters, Application, CallbackQueryHandler, MessageHandler

from mediabot.features.instagram.handlers import instagram_handle_collection_item_download_callback_query, \
    instagram_handle_link_message, instagram_handle_username_stories_message, instagram_handle_music_button

class InstagramFeature:
  instagram_music_handler = CallbackQueryHandler(
    pattern=r"^instagram_music12:",
    callback=instagram_handle_music_button
  )
  instagram_link_handler = MessageHandler(filters.Regex(r"^((?:https?://)?(?:www.)?instagram.com/?([a-zA-Z0-9._-]+)?/([p]+)?([reel]+)?([tv]+)?([stories]+)?/([a-zA-Z0-9-_.]+)/?([0-9]+)?)") & filters.ChatType.PRIVATE, instagram_handle_link_message)
  instagram_username_stories_message_handler = MessageHandler(filters.Regex(r"^@[\w](?!.*?\.{2})[\w.]{1,28}[\w]$") & filters.ChatType.PRIVATE, instagram_handle_username_stories_message)
  instagram_collection_item_callback_query_handler = CallbackQueryHandler(instagram_handle_collection_item_download_callback_query, "^instagram_download_([a-zA-Z0-9]+)_([0-9]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(InstagramFeature.instagram_link_handler)
    botapp.add_handler(InstagramFeature.instagram_collection_item_callback_query_handler)
    botapp.add_handler(InstagramFeature.instagram_username_stories_message_handler)
    botapp.add_handler(InstagramFeature.instagram_music_handler)
