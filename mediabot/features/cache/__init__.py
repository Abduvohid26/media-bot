from telegram.ext import Application, CommandHandler

from mediabot.features.cache.handlers import cache_cache_command_handler

class CacheFeature:
  cache_command_handler = CommandHandler("cache", cache_cache_command_handler)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(CacheFeature.cache_command_handler)
