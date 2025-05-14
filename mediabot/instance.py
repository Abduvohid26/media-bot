import json
import typing
import time
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, Defaults, ContextTypes
from telegram.request import HTTPXRequest
from telegram.constants import ChatType

from mediabot.features.account import AccountFeature
from mediabot.features.group import GroupFeature
from mediabot.features.account.model import Account
from mediabot.features.advertisement import AdvertisementFeature
from mediabot.features.broadcast import BroadcastFeature
from mediabot.features.command import CommandFeature
from mediabot.features.instagram import InstagramFeature
from mediabot.features.join_request import JoinRequestFeature
from mediabot.features.language import LanguageFeature
from mediabot.features.message import MessageFeature
from mediabot.features.referral import ReferralFeature
from mediabot.features.required_join import RequiredJoinFeature
from mediabot.features.sys import SysFeature
from mediabot.features.tiktok import TikTokFeature
from mediabot.features.cache import CacheFeature
from mediabot.features.track import TrackRecognizeFromVideoNoteFeature, TrackSearchFeature, TrackDownloadFeature, \
    TrackPopularTracksFeature, TrackRecognizeFromVoiceFeature, TrackRecognizeFromVideoFeature, TrackRecognizeFromAudioFeature
from mediabot.features.track.handlers import track_handle_download_web
from mediabot.features.youtube import YouTubeSearchFeature, YouTubeLinkFeature, YouTubeDownloadFeature
from mediabot.features.twitter import TwitterFeature
from mediabot.features.likee import LikeeFeature
from mediabot.features.tumblr import TumblrFeature
from mediabot.features.pinterest import PinterestFeature
from mediabot.features.facebook import FacebookFeature
from mediabot.features.instance import InstanceFeature
from mediabot.features.control_panel import ControlPanelFeature
from mediabot.features.instance.model import INSTANCE_CONTEXT, _Instance, INSTANCE_ID_CONTEXT, INSTANCE_LOGGER_CONTEXT, Instance as InstanceModel
from mediabot.features.command.model import Command
import mediabot.features.broadcast.handlers as broadcast_feature_handlers

from mediabot.handlers.error import error_handle_error
from mediabot.logger import CustomJsonFormatter, MergingLoggerAdapter
from mediabot.context import Context
from mediabot.env import CONCURRENT_UPDATES, TELEGRAM_BOT_WEBHOOK_URL, TELEGRAM_BOT_API_BASE_URL

BOTAPP_DEFAULTS = Defaults(parse_mode="HTML", disable_web_page_preview=True)
MAX_REQUEST_TIMESTAMPS = 128

import logging
import logging.handlers

class Instance:
  botapp: Application

  instance: _Instance

  logger: logging.LoggerAdapter

  # stores last sent request timestamps
  _request_timestamps: typing.List[int] = []

  def __init__(self, instance: _Instance):
    context_types = ContextTypes(context=Context)

    concurrent_updates = instance.actions_per_second \
        if instance.actions_per_second != -1 else CONCURRENT_UPDATES

    request = HTTPXRequest(connection_pool_size=1024, pool_timeout=4, read_timeout=32, write_timeout=32)

    botapp = ApplicationBuilder() \
      .defaults(BOTAPP_DEFAULTS) \
      .context_types(context_types) \
      .token(instance.token) \
      .base_url(TELEGRAM_BOT_API_BASE_URL) \
      .base_file_url("") \
      .updater(None) \
      .request(request) \
      .local_mode(True) \
      .concurrent_updates(True) \
      .build()

    botapp.bot_data.setdefault(INSTANCE_ID_CONTEXT, instance.id)
    botapp.bot_data.setdefault(INSTANCE_CONTEXT, self)
    self.instance = instance
    self.botapp = botapp

    self._register_global_handlers()
    self._register_features()

  def _register_log_handlers(self):
    logHandler = logging.handlers.RotatingFileHandler(f"logs/{self.instance.username}.log", maxBytes=1048576, backupCount=1)
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(instance)s %(action)s')
    logHandler.setFormatter(formatter)
    logger = logging.Logger(self.instance.username, logging.DEBUG)
    logger_adapter = MergingLoggerAdapter(logger, dict(instance = self.instance.username))
    logger.addHandler(logHandler)

    self.botapp.bot_data.setdefault(INSTANCE_LOGGER_CONTEXT, logger_adapter)
    self.logger = logger_adapter

  def _register_error_handlers(self) -> None:
    self.botapp.add_error_handler(error_handle_error)

  async def process_update(self, update: dict) -> None:
    assert self.botapp

    deserialized_update = Update.de_json(data=update, bot=self.botapp.bot)
    assert deserialized_update

    self.logger.debug(None, extra={"action": "UPDATE", "update": json.dumps(update)})

    self.botapp.update_queue.put_nowait(deserialized_update)

    if deserialized_update.effective_chat and deserialized_update.effective_chat.type == ChatType.PRIVATE:
      self._request_timestamps.append(int(time.time()))
      self._request_timestamps = self._request_timestamps[-MAX_REQUEST_TIMESTAMPS:]

      await InstanceModel.mark_request_for_today(self.instance.id, deserialized_update.effective_user.id)

  def get_request_per_second(self):
    # because you can't iterate over an array and change its size at the same time, so we have to copy the whole array
    request_timestamps = self._request_timestamps.copy()

    return len([request_timestamp for request_timestamp in request_timestamps if time.time() - request_timestamp <= 1])

  async def process_track_download_web(self, chat_id: int, user_id: int, track_id: str):
    context = Context(self.botapp, chat_id, user_id)
    account = await Account.get(self.instance.id, user_id)
    context.account = account
    context.instance = self.instance
    await track_handle_download_web(context, chat_id, user_id, track_id)

  async def process_video_download_web(self, chat_id: int, user_id: int, video_id: str):
    context = Context(self.botapp, chat_id, user_id)
    account = await Account.get(self.instance.id, user_id)
    context.account = account
    context.instance = self.instance
    await track_handle_download_web(context, chat_id, user_id, video_id)

  def _register_features(self):
    assert self.botapp

    InstanceFeature.register_handlers(self.botapp)
    AccountFeature.register_handlers(self.botapp)
    GroupFeature.register_handlers(self.botapp)

    CacheFeature.register_handlers(self.botapp)

    if self.instance.broadcast_feature_enabled:
      BroadcastFeature.register_features(self.botapp)
    
    if self.instance.command_feature_enabled:
      CommandFeature.register_handlers(self.botapp)

    if self.instance.required_join_feature_enabled:
      RequiredJoinFeature.register_handlers(self.botapp)

    if self.instance.advertisement_feature_enabled:
      AdvertisementFeature.register_handlers(self.botapp)

    if self.instance.join_request_feature_enabled:
      JoinRequestFeature.register_handlers(self.botapp)

    ReferralFeature.register_handler(self.botapp)
    MessageFeature.register_handlers(self.botapp)
    ControlPanelFeature.register_handlers(self.botapp)

    SysFeature.register_handlers(self.botapp)
    LanguageFeature.register_handlers(self.botapp)

    if self.instance.twitter_feature_enabled:
      TwitterFeature.register_handlers(self.botapp)

    if self.instance.likee_feature_enabled:
      LikeeFeature.register_handlers(self.botapp)

    if self.instance.tumblr_feature_enabled:
      TumblrFeature.register_handlers(self.botapp)

    if self.instance.pinterest_feature_enabled:
      PinterestFeature.register_handlers(self.botapp)

    if self.instance.instagram_feature_enabled:
      InstagramFeature.register_handlers(self.botapp)

    if self.instance.tiktok_feature_enabled:
      TikTokFeature.register_handlers(self.botapp)

    if self.instance.facebook_feature_enabled:
      FacebookFeature.register_handlers(self.botapp)

    if self.instance.youtube_link_feature_enabled:
      YouTubeLinkFeature.register_handlers(self.botapp)

    if self.instance.youtube_search_feature_enabled:
      YouTubeSearchFeature.register_handlers(self.botapp)

    if self.instance.youtube_download_feature_enabled:
      YouTubeDownloadFeature.register_handlers(self.botapp)

    if self.instance.track_search_feature_enabled:
      TrackSearchFeature.register_handlers(self.botapp)

    if self.instance.track_download_feature_enabled:
      TrackDownloadFeature.register_handlers(self.botapp)

    TrackPopularTracksFeature.register_handlers(self.botapp)

    if self.instance.track_recognize_from_voice_feature_enabled:
      TrackRecognizeFromVoiceFeature.register_handlers(self.botapp)

    if self.instance.track_recognize_from_video_feature_enabled:
      TrackRecognizeFromVideoFeature.register_handlers(self.botapp)

    if self.instance.track_recognize_from_video_note_feature_enabled:
      TrackRecognizeFromVideoNoteFeature.register_handlers(self.botapp)

    if self.instance.track_recognize_from_audio_feature_enabled:
      TrackRecognizeFromAudioFeature.register_handlers(self.botapp)

  def _register_global_handlers(self):
    self._register_log_handlers()
    self._register_error_handlers()

  async def bootstrap(self) -> None:
    assert self.botapp

    bot = typing.cast(Bot, self.botapp.bot)

    await self.botapp.initialize()
    await self.botapp.start()

    # webhook_info = await bot.get_webhook_info()
    webhook_url = TELEGRAM_BOT_WEBHOOK_URL.format(self.instance.id)

    await bot.set_webhook(webhook_url,
      allowed_updates=[
        Update.MESSAGE,
        Update.CALLBACK_QUERY,
        Update.CHAT_MEMBER,
        Update.MY_CHAT_MEMBER,
        Update.CHAT_JOIN_REQUEST,
        Update.INLINE_QUERY,
        Update.CHOSEN_INLINE_RESULT
      ],
      drop_pending_updates=True,
      max_connections=100
    )

    await self.sync_commands()
    await self.run_pending_broadcasts()

  async def run_pending_broadcasts(self):
    await broadcast_feature_handlers.broadcast_run_running_broadcasts(self.instance.id, self.botapp, self.instance)

  async def sync_commands(self):
    try:
      await Command.sync_commands(self.instance.id, self.botapp.bot)
    except:
      pass

  async def close(self) -> None:
    assert self.botapp

    bot = typing.cast(Bot, self.botapp.bot)

    await bot.delete_webhook(drop_pending_updates=True)

    await self.botapp.stop()
