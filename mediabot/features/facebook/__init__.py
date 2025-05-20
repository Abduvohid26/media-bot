from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler

from mediabot.features.facebook.handlers import (
    facebook_handle_link_message,
    facebook_handle_download_callback_query
)

class FacebookFeature:
    facebook_link_message_handler = MessageHandler(
        filters.Regex(r"https?://(?:www\.)?(facebook|fb)\.com/[^\s]+") & filters.ChatType.PRIVATE,
        facebook_handle_link_message
    )

    facebook_download_callback_query_handler = CallbackQueryHandler(
        facebook_handle_download_callback_query,
        pattern="^facebook_download_([0-9]+)_(.+)$"
    )

    @staticmethod
    def register_handlers(botapp: Application):
        botapp.add_handler(FacebookFeature.facebook_link_message_handler)
        botapp.add_handler(FacebookFeature.facebook_download_callback_query_handler)
