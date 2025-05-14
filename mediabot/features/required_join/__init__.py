from telegram.ext import filters, Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, ChatMemberHandler

from mediabot.features.required_join.handlers import required_join_handle_create_callback_query, required_join_handle_create_cancel_message, required_join_handle_create_target_chat_message, \
    required_join_handle_delete_callback_query, required_join_handle_edit_end_time, required_join_handle_edit_end_time_enter, required_join_handle_edit_join_link_callback_query, \
    required_join_handle_edit_join_link_enter, required_join_handle_edit_schedule_count_callback_query, required_join_handle_edit_schedule_count_enter, \
    required_join_handle_edit_target_chat_callback_query, required_join_handle_edit_target_chat_enter, required_join_handle_edit_target_join_count_callback_query, \
    required_join_handle_edit_target_join_count_enter, required_join_handle_required_join_callback_query, required_join_handle_required_joins_callback_query, \
    required_join_handle_toggle_is_enabled_callback_query, required_join_handle_toggle_is_optional_callback_query, required_join_handle_toggle_kind_callback_query, chat_member_handle
from mediabot.features.required_join.model import REQUIRED_JOIN_STATE_EDIT_END_TIME_ENTER, REQUIRED_JOIN_STATE_EDIT_JOIN_LINK_ENTER, REQUIRED_JOIN_STATE_EDIT_SCHEDULE_COUNT_ENTER, \
    REQUIRED_JOIN_STATE_EDIT_TARGET_CHAT_ENTER, REQUIRED_JOIN_STATE_EDIT_TARGET_COUNT_ENTER, REQUIRED_JOIN_STATE_CREATE_TARGET_CHAT

class RequiredJoinFeature:
  required_joins_callback_query_handler = CallbackQueryHandler(required_join_handle_required_joins_callback_query, "^required_join$")
  required_join_callback_query_handler = CallbackQueryHandler(required_join_handle_required_join_callback_query, "^required_join_([0-9]+)$")
  required_join_delete_callback_query_handler = CallbackQueryHandler(required_join_handle_delete_callback_query, "^required_join_delete_([0-9]+)$")
  required_join_toggle_is_optional_callback_query_handler = CallbackQueryHandler(required_join_handle_toggle_is_optional_callback_query, "^required_join_toggle_is_optional_([0-9]+)_([0-1])$")
  required_join_toggle_is_enabled_callback_query_handler = CallbackQueryHandler(required_join_handle_toggle_is_enabled_callback_query, "^required_join_toggle_is_enabled_([0-9]+)_([0-1])$")
  required_join_toggle_kind_callback_query_handler = CallbackQueryHandler(required_join_handle_toggle_kind_callback_query, "^required_join_toggle_kind_([0-9]+)_([0-1])$")
  chat_member_handler = ChatMemberHandler(chat_member_handle, ChatMemberHandler.CHAT_MEMBER)

  edit_target_join_count_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_edit_target_join_count_callback_query, "^required_join_edit_target_join_count_([0-9]+)")
  ], states={
    REQUIRED_JOIN_STATE_EDIT_TARGET_COUNT_ENTER: [
      MessageHandler(filters.TEXT, required_join_handle_edit_target_join_count_enter)
    ]
  }, fallbacks=[])

  edit_schedule_count_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_edit_schedule_count_callback_query, "^required_join_edit_schedule_count_([0-9]+)")
  ], states={
    REQUIRED_JOIN_STATE_EDIT_SCHEDULE_COUNT_ENTER: [
      MessageHandler(filters.TEXT, required_join_handle_edit_schedule_count_enter)
    ]
  }, fallbacks=[])

  edit_join_link_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_edit_join_link_callback_query, "^required_join_edit_join_link_([0-9]+)")
  ], states={
    REQUIRED_JOIN_STATE_EDIT_JOIN_LINK_ENTER: [
      MessageHandler(filters.TEXT, required_join_handle_edit_join_link_enter)
    ]
  }, fallbacks=[])

  edit_target_chat_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_edit_target_chat_callback_query, "^required_join_edit_target_chat_([0-9]+)")
  ], states={
    REQUIRED_JOIN_STATE_EDIT_TARGET_CHAT_ENTER: [
      MessageHandler(filters.TEXT, required_join_handle_edit_target_chat_enter)
    ]
  }, fallbacks=[])

  edit_end_time_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_edit_end_time, "^required_join_edit_end_time_([0-9]+)")
  ], states={
    REQUIRED_JOIN_STATE_EDIT_END_TIME_ENTER: [
      MessageHandler(filters.TEXT, required_join_handle_edit_end_time_enter)
    ]
  }, fallbacks=[])

  create_required_join_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(required_join_handle_create_callback_query, "^required_join_create$")
  ],
  states={
    REQUIRED_JOIN_STATE_CREATE_TARGET_CHAT: [
      MessageHandler(filters.TEXT & (~filters.COMMAND), required_join_handle_create_target_chat_message)
    ]
  }, fallbacks=[CommandHandler("cancel", required_join_handle_create_cancel_message)])

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(RequiredJoinFeature.required_join_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.required_joins_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.required_join_delete_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.required_join_toggle_is_optional_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.required_join_toggle_is_enabled_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.required_join_toggle_kind_callback_query_handler)
    botapp.add_handler(RequiredJoinFeature.chat_member_handler)
    botapp.add_handler(RequiredJoinFeature.edit_target_join_count_conversation_handler)
    botapp.add_handler(RequiredJoinFeature.edit_schedule_count_conversation_handler)
    botapp.add_handler(RequiredJoinFeature.edit_join_link_conversation_handler)
    botapp.add_handler(RequiredJoinFeature.edit_end_time_conversation_handler)
    botapp.add_handler(RequiredJoinFeature.edit_target_chat_conversation_handler)
    botapp.add_handler(RequiredJoinFeature.create_required_join_conversation_handler)
