from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler

from mediabot.features.facebook.handlers import (
    facebook_handle_link_message,
    facebook_handle_collection_item_download_callback_query
)

class FacebookFeature:
    facebook_link_message_handler = MessageHandler(
        filters.Regex(r"https?://(?:www\.)?(facebook|fb)\.com/[^\s]+") & filters.ChatType.PRIVATE,
        facebook_handle_link_message
    )

    instagram_collection_item_callback_query_handler = CallbackQueryHandler(facebook_handle_collection_item_download_callback_query, "^facebook_download_([a-zA-Z0-9]+)_([0-9]+)$")



    @staticmethod
    def register_handlers(botapp: Application):
        botapp.add_handler(FacebookFeature.facebook_link_message_handler)
        botapp.add_handler(FacebookFeature.instagram_collection_item_callback_query_handler)
