from telegram import Update
from telegram.ext import filters, Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, TypeHandler

from mediabot.features.referral.handlers import referral_handle_create_callback_query, referral_handle_create_enter_message, referral_handle_delete, \
    referral_handle_create_cancel, referral_handle_referral_callback_query, referral_handle_referrals_callback_query, referral_handle_update
from mediabot.features.referral.model import CREATE_REFERRAL_STATE_ENTER

class ReferralFeature:
  referrals_callback_query_handler = CallbackQueryHandler(referral_handle_referrals_callback_query, f"^referral$")
  referral_callback_query_handler = CallbackQueryHandler(referral_handle_referral_callback_query, f"^referral_([0-9]+)$")

  referral_delete_callback_query_handler = CallbackQueryHandler(referral_handle_delete, f"^referral_delete_([0-9]+)$")
  referral_create_conversation_handler = ConversationHandler(entry_points=[
    CallbackQueryHandler(referral_handle_create_callback_query, "^referral_create$")
  ], states={
    CREATE_REFERRAL_STATE_ENTER: [
      MessageHandler(filters.TEXT & (~filters.COMMAND), referral_handle_create_enter_message)
    ]
  }, fallbacks=[CommandHandler("cancel", referral_handle_create_cancel)])  # TODO(mhw0): add cancel command?

  referral_update_type_handler_handler = MessageHandler(filters.COMMAND, referral_handle_update)

  @staticmethod
  def register_handler(botapp: Application):
    botapp.add_handler(ReferralFeature.referral_update_type_handler_handler, -7)
    botapp.add_handler(ReferralFeature.referral_callback_query_handler)
    botapp.add_handler(ReferralFeature.referrals_callback_query_handler)
    botapp.add_handler(ReferralFeature.referrals_callback_query_handler)

    botapp.add_handler(ReferralFeature.referral_delete_callback_query_handler)
    botapp.add_handler(ReferralFeature.referral_create_conversation_handler)
