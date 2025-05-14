from telegram import Update
from telegram.ext import Application, TypeHandler, ChatMemberHandler

from mediabot.features.account.handlers import account_update_handler, account_my_chat_member_handler

class AccountFeature:
  account_update_type_handler_handler = TypeHandler(Update, account_update_handler)
  account_my_chat_member_handler = ChatMemberHandler(account_my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(AccountFeature.account_update_type_handler_handler, -9)
    botapp.add_handler(AccountFeature.account_my_chat_member_handler, -8)
