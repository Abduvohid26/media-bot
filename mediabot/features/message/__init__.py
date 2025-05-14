from telegram.ext import filters, Application, CallbackQueryHandler, MessageHandler, ConversationHandler

from mediabot.features.message.handlers import message_handle_language_edit_callback_query, message_handle_language_edit_enter_message, \
    message_handle_message_add_callback_query, message_handle_message_add_enter_message, message_handle_message_callback_query, \
    message_handle_message_delete_callback_query, message_handle_message_edit_callback_query, message_handle_message_edit_enter_message, \
    message_handle_message_is_after_join_toggle_callback_query, message_handle_message_is_attach_toggle_callback_query, \
    message_handle_message_is_forward_toggle_callback_query, message_handle_messages_callback_query
from mediabot.features.message.model import MESSAGE_STATE_LANGUAGE_EDIT, MESSAGE_STATE_MESSAGE_ADD, MESSAGE_STATE_MESSAGE_EDIT

class MessageFeature:
  messages_callback_query_handler = CallbackQueryHandler(message_handle_messages_callback_query, "^messages_([0-9]+)_([0-9]+)$")
  message_callback_query_handler = CallbackQueryHandler(message_handle_message_callback_query, "^message_([0-9]+)_([0-9]+)_([0-9]+)$")
  message_delete_callback_query_handler = CallbackQueryHandler(message_handle_message_delete_callback_query, "^message_delete_([0-9]+)_([0-9]+)_([0-9]+)$")
  message_is_attach_toggle_callback_query_handler = CallbackQueryHandler(message_handle_message_is_attach_toggle_callback_query, "^message_is_attach_toggle_([0-9]+)_([0-9]+)_([0-9]+)_([0-9]+)$")
  message_is_forward_toggle_callback_query_handler = CallbackQueryHandler(message_handle_message_is_forward_toggle_callback_query, "^message_is_forward_toggle_([0-9]+)_([0-9]+)_([0-9]+)_([0-9]+)$")
  message_is_after_join_toggle_callback_query_handler = CallbackQueryHandler(message_handle_message_is_after_join_toggle_callback_query, "^message_is_after_join_toggle_([0-9]+)_([0-9]+)_([0-9]+)_([0-9]+)$")
  edit_message_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(message_handle_message_edit_callback_query, "^message_message_edit_([0-9]+)_([0-9]+)_([0-9]+)")
  ], states={
    MESSAGE_STATE_MESSAGE_EDIT: [
      MessageHandler(filters.ALL, message_handle_message_edit_enter_message)
    ]
  }, fallbacks=[], per_chat=True)
  edit_language_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(message_handle_language_edit_callback_query, "^message_language_edit_([0-9]+)")
  ], states={
    MESSAGE_STATE_LANGUAGE_EDIT: [
      MessageHandler(filters.ALL, message_handle_language_edit_enter_message)
    ]
  }, fallbacks=[])
  add_message_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(message_handle_message_add_callback_query, "^message_add_([0-9]+)_([0-9]+)$")
  ], states={
    MESSAGE_STATE_MESSAGE_ADD: [
      MessageHandler(filters.ALL, message_handle_message_add_enter_message)
    ]
  }, fallbacks=[])

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(MessageFeature.messages_callback_query_handler)
    botapp.add_handler(MessageFeature.message_callback_query_handler)
    botapp.add_handler(MessageFeature.message_delete_callback_query_handler)
    botapp.add_handler(MessageFeature.message_is_attach_toggle_callback_query_handler)
    botapp.add_handler(MessageFeature.message_is_forward_toggle_callback_query_handler)
    botapp.add_handler(MessageFeature.message_is_after_join_toggle_callback_query_handler)
    botapp.add_handler(MessageFeature.edit_message_conversation_handler)
    botapp.add_handler(MessageFeature.edit_language_conversation_handler)
    botapp.add_handler(MessageFeature.add_message_conversation_handler)
