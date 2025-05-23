from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler

from mediabot.features.youtube_voice.handlers import youtube_voice_handle_link_message

class YouTubeVoiceSearchFeature:
    youtube_search_message_handler = MessageHandler(
        filters.VOICE & (~filters.COMMAND) & filters.ChatType.PRIVATE,
        youtube_voice_handle_link_message
    )

    @staticmethod
    def register_handlers(botapp: Application):
        botapp.add_handler(YouTubeVoiceSearchFeature.youtube_search_message_handler)
