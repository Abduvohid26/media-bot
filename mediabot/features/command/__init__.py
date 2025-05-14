from telegram.ext import Application
from telegram.ext import filters, Application, CallbackQueryHandler, ConversationHandler, MessageHandler

from mediabot.features.command.handlers import command_handle_command_callback_query, command_handle_command_create_callback_query, \
    command_handle_command_create_name_message, command_handle_command_delete_callback_query, command_handle_command_is_enabled_toggle, \
    command_handle_commands_callback_query, command_handle_dynamic_command_message
from mediabot.features.command.model import COMMAND_STATE_NAME

COMMAND_REGEX_GROUP = 1

class CommandFeature:
  commands_callback_query_handler = CallbackQueryHandler(command_handle_commands_callback_query, "^command$")
  command_callback_query_handler = CallbackQueryHandler(command_handle_command_callback_query, "^command_([0-9]+)$")
  commands_is_enabled_toggle_callback_query_handler = CallbackQueryHandler(command_handle_command_is_enabled_toggle, f"^command_is_enabled_toggle_([0-9]+)_([0-1])$")
  command_delete_callback_query_handler = CallbackQueryHandler(command_handle_command_delete_callback_query, "^command_delete_([0-9]+)$")
  command_dynamic_handler_message_handler = MessageHandler(filters.COMMAND, command_handle_dynamic_command_message)
  create_command_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(command_handle_command_create_callback_query, "^command_create$")
  ], states={
    COMMAND_STATE_NAME: [
      MessageHandler(filters.TEXT, command_handle_command_create_name_message)
    ]
  }, fallbacks=[])  # TODO(mhw0): add cancel command?

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(CommandFeature.commands_callback_query_handler)
    botapp.add_handler(CommandFeature.command_callback_query_handler)
    botapp.add_handler(CommandFeature.commands_is_enabled_toggle_callback_query_handler)
    botapp.add_handler(CommandFeature.command_delete_callback_query_handler)
    botapp.add_handler(CommandFeature.command_dynamic_handler_message_handler, COMMAND_REGEX_GROUP)
    botapp.add_handler(CommandFeature.create_command_conversation_handler)
