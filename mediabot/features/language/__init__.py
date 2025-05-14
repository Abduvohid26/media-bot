from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, filters, MessageHandler
from mediabot.features.language.handlers import language_handle_cancel_command, language_handle_change_language_command, \
    language_handle_change_language_update_callback_query, language_handle_create_callback_query, language_handle_create_code_message, language_handle_create_name_message, \
    language_handle_delete_callback_query, language_handle_languages_callback_query
from mediabot.features.language.model import LANGUAGE_STATE_CREATE_NAME, LANGUAGE_STATE_CREATE_CODE

class LanguageFeature:
  language_change_language_command_handler = CommandHandler("change_language", language_handle_change_language_command)
  language_change_language_update_callback_query_handler = CallbackQueryHandler(language_handle_change_language_update_callback_query, "^language_update_([0-9]+)$")
  languages_callback_query_handler = CallbackQueryHandler(language_handle_languages_callback_query, "^language$")
  languages_delete_callback_query_handler = CallbackQueryHandler(language_handle_delete_callback_query, "^language_delete_([0-9]+)$")
  language_create_conversation_handler =  ConversationHandler(entry_points=[
      CallbackQueryHandler(language_handle_create_callback_query, "^language_create$")
    ], states={
      LANGUAGE_STATE_CREATE_NAME: [
        MessageHandler(filters.TEXT & (~filters.COMMAND), language_handle_create_name_message)
      ],
      LANGUAGE_STATE_CREATE_CODE: [
        MessageHandler(filters.TEXT & (~filters.COMMAND), language_handle_create_code_message)
      ]
    }, fallbacks=[CommandHandler("cancel", language_handle_cancel_command)])

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(LanguageFeature.language_change_language_command_handler)
    botapp.add_handler(LanguageFeature.language_change_language_update_callback_query_handler)
    botapp.add_handler(LanguageFeature.languages_callback_query_handler)
    botapp.add_handler(LanguageFeature.languages_delete_callback_query_handler)
    botapp.add_handler(LanguageFeature.language_create_conversation_handler)
