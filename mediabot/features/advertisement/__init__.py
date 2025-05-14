from telegram.ext import Application, CallbackQueryHandler, filters, ConversationHandler, MessageHandler

from mediabot.features.advertisement.handlers import advertisement_handle_advertisement, advertisement_handle_advertisement_delete, \
    advertisement_handle_advertisement_is_enabled_toggle, advertisement_handle_advertisement_kind_toggle, advertisement_handle_advertisement_message_seen_clear, \
    advertisement_handle_advertisements_callback_query, advertisement_handle_create_callback_query, advertisement_handle_create_name
from mediabot.features.advertisement.model import ADVERTISEMENT_STATE_CREATE_NAME

class AdvertisementFeature:
  advertisements_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisements_callback_query, "^advertisement$")
  advertisement_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisement, "^advertisement_([0-9]+)$")
  advertisement_delete_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisement_delete, "^advertisement_delete_([0-9]+)$")
  advertisement_is_enabled_toggle_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisement_is_enabled_toggle, "^advertisement_is_enabled_toggle_([0-9]+)_([0-1])$")
  advertisement_kind_toggle_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisement_kind_toggle, "^advertisement_kind_toggle_([0-9]+)_([0-9]+)$")
  advertisement_message_seen_clear_callback_query_handler = CallbackQueryHandler(advertisement_handle_advertisement_message_seen_clear, "^advertisement_message_seen_clear_([0-9]+)$")

  advertisement_create_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(advertisement_handle_create_callback_query, "^advertisement_create$")
  ],
  states={
    ADVERTISEMENT_STATE_CREATE_NAME: [
      MessageHandler(filters.TEXT & (~filters.COMMAND), advertisement_handle_create_name)
    ]
  }, fallbacks=[])

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(AdvertisementFeature.advertisements_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_delete_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_is_enabled_toggle_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_kind_toggle_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_message_seen_clear_callback_query_handler)
    botapp.add_handler(AdvertisementFeature.advertisement_create_conversation_handler)
