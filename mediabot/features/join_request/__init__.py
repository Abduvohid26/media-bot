from telegram.ext import filters, Application, CallbackQueryHandler, ConversationHandler, MessageHandler, ChatJoinRequestHandler

from mediabot.features.join_request.handlers import join_request_handle_accept_callback_query, join_request_handle_chat_join_request, \
    join_request_handle_create_callback_query, join_request_handle_create_enter_message, join_request_handle_decline_callback_query, \
    join_request_handle_delete_callback_query, join_request_handle_join_request_callback_query, join_request_handle_join_requests_callback_query, \
    join_request_handle_reset_callback_query, join_request_handle_toggle_is_autoapprove_callback_query, join_request_handle_toggle_is_autodecline_callback_query
from mediabot.features.join_request.model import JOIN_REQUEST_STATE_CREATE

class JoinRequestFeature:
  join_requests_callback_query_handler = CallbackQueryHandler(join_request_handle_join_requests_callback_query, "^join_requests$")
  join_request_callback_query_handler = CallbackQueryHandler(join_request_handle_join_request_callback_query, "^join_request_([0-9]+)$")
  join_request_reset_callback_query_handler = CallbackQueryHandler(join_request_handle_reset_callback_query, "^join_request_reset_([0-9]+)$")
  join_request_accept_callback_query_handler = CallbackQueryHandler(join_request_handle_accept_callback_query, "^join_request_accept_([0-9]+)$")
  join_request_decline_callback_query_handler = CallbackQueryHandler(join_request_handle_decline_callback_query, "^join_request_decline_([0-9]+)$")
  join_request_toggle_is_autoapprove_callback_query_handler = CallbackQueryHandler(join_request_handle_toggle_is_autoapprove_callback_query, "^join_request_toggle_is_autoapprove_([0-9]+)_([0-1])$")
  join_request_toggle_is_autodecline_callback_query_handler = CallbackQueryHandler(join_request_handle_toggle_is_autodecline_callback_query, "^join_request_toggle_is_autodecline_([0-9]+)_([0-1])$")
  join_request_delete_callback_query_handler = CallbackQueryHandler(join_request_handle_delete_callback_query, "^join_request_delete_([0-9]+)$")
  join_request_chat_join_request_handler = ChatJoinRequestHandler(join_request_handle_chat_join_request)
  join_request_create_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(join_request_handle_create_callback_query, "^join_request_create$")
  ], states={
    JOIN_REQUEST_STATE_CREATE: [
      MessageHandler(filters.TEXT, join_request_handle_create_enter_message)
    ]
  }, fallbacks=[])

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(JoinRequestFeature.join_requests_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_reset_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_accept_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_decline_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_toggle_is_autoapprove_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_toggle_is_autodecline_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_delete_callback_query_handler)
    botapp.add_handler(JoinRequestFeature.join_request_create_conversation_handler)
    botapp.add_handler(JoinRequestFeature.join_request_chat_join_request_handler)
