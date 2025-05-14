from telegram.ext import filters, Application, CallbackQueryHandler, ConversationHandler, MessageHandler

from mediabot.features.broadcast.handlers import broadcast_handle_broadcast_callback_query, \
    broadcast_handle_broadcasts_callback_query, broadcast_handle_create_callback_query, broadcast_handle_create_is_group, \
    broadcast_handle_create_is_silent, broadcast_handle_create_jobs, broadcast_handle_create_message, \
    broadcast_handle_create_message_language, broadcast_handle_create_name, broadcast_handle_delete_callback_query, \
    broadcast_handle_message_show_callback_query, broadcast_handle_status_toggle_callback_query
from mediabot.features.broadcast.model import BROADCAST_STATE_CREATE_IS_GROUP, BROADCAST_STATE_CREATE_IS_SILENT, \
    BROADCAST_STATE_CREATE_JOBS, BROADCAST_STATE_CREATE_LANGUAGE, BROADCAST_STATE_CREATE_MESSAGE, BROADCAST_STATE_CREATE_NAME

class BroadcastFeature:
  broadcasts_callback_query_haandler = CallbackQueryHandler(broadcast_handle_broadcasts_callback_query, "^broadcast$")
  broadcast_callback_query_haandler = CallbackQueryHandler(broadcast_handle_broadcast_callback_query, "^broadcast_([0-9]+)$")
  broadcast_delete_callback_query_haandler = CallbackQueryHandler(broadcast_handle_delete_callback_query, "^broadcast_delete_([0-9]+)$")
  broadcast_message_show_callback_query_haandler = CallbackQueryHandler(broadcast_handle_message_show_callback_query, "^broadcast_message_show_([0-9]+)$")
  broadcast_status_toggle_callback_query_haandler = CallbackQueryHandler(broadcast_handle_status_toggle_callback_query, "^broadcast_status_toggle_([0-9]+)$")
  broadcast_create_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(broadcast_handle_create_callback_query, "^broadcast_create$")
  ], states={
    BROADCAST_STATE_CREATE_NAME: [
      MessageHandler(filters.TEXT, broadcast_handle_create_name)
    ],
    BROADCAST_STATE_CREATE_MESSAGE: [
      MessageHandler(filters.ALL, broadcast_handle_create_message)
    ],
    BROADCAST_STATE_CREATE_LANGUAGE: [
      MessageHandler(filters.TEXT, broadcast_handle_create_message_language)
    ],
    BROADCAST_STATE_CREATE_JOBS: [
      MessageHandler(filters.TEXT, broadcast_handle_create_jobs)
    ],
    BROADCAST_STATE_CREATE_IS_GROUP: [
      MessageHandler(filters.ALL, broadcast_handle_create_is_group)
    ],
    BROADCAST_STATE_CREATE_IS_SILENT: [
      MessageHandler(filters.ALL, broadcast_handle_create_is_silent)
    ]
  }, fallbacks=[])

  @staticmethod
  def register_features(botapp: Application):
    botapp.add_handler(BroadcastFeature.broadcasts_callback_query_haandler)
    botapp.add_handler(BroadcastFeature.broadcast_callback_query_haandler)
    botapp.add_handler(BroadcastFeature.broadcast_delete_callback_query_haandler)
    botapp.add_handler(BroadcastFeature.broadcast_message_show_callback_query_haandler)
    botapp.add_handler(BroadcastFeature.broadcast_status_toggle_callback_query_haandler)
    botapp.add_handler(BroadcastFeature.broadcast_create_conversation_handler)
