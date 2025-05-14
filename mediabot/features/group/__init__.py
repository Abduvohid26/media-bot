from telegram.ext import Application, TypeHandler
from telegram import Update

from mediabot.features.group.handlers import group_update_handler

class GroupFeature:
  group_update_type_handler_handler = TypeHandler(Update, group_update_handler)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(GroupFeature.group_update_type_handler_handler, -8)
