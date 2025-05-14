from telegram import Update
from telegram.ext import Application, TypeHandler, MessageHandler

from mediabot.features.instance.handlers import instance_update_handler

class InstanceFeature:
  instance_update_type_handler_handler = TypeHandler(Update, instance_update_handler)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(InstanceFeature.instance_update_type_handler_handler, -100)
