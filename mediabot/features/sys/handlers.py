import os
import psutil
import typing
import datetime
import math
import sys
import pathlib
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from ...utils import get_local_path_of

from mediabot.context import Context
from mediabot.database.connection import get_pool_stats
from mediabot.decorators import only_sys
from mediabot.features.command.model import Command
from mediabot.features.sys.model import Sys
from mediabot.features.instance.model import Instance, InstanceFeatures

def convert_size(size_bytes):
  if size_bytes == 0:
    return "0B"

  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])

@only_sys
async def sys_handle_info(update: Update, context: Context) -> None:
  assert update.message

  process = psutil.Process(os.getpid())
  vmem = psutil.virtual_memory()
  networkio = psutil.net_io_counters()
  disk_path = "/Users" if sys.platform == "darwin" else "/home"
  disk = psutil.disk_usage(disk_path)

  sys_info_text = f"<b>Process info:</b> (<b>{process.pid}</b>)\n"
  sys_info_text += f"- CPU utilization: <b>{psutil.cpu_percent()}%</b> / <b>{psutil.cpu_count()} unit</b>\n"
  sys_info_text += f"- Memory: <b>{convert_size(vmem.used)}</b> / <b>{convert_size(vmem.total)}</b>\n"
  sys_info_text += f"- Bandwidth: <b>↑ {convert_size(networkio.bytes_sent)}</b> / <b>↓ {convert_size(networkio.bytes_recv)}</b>\n"
  sys_info_text += f"- Disk: <b>{convert_size(disk.used)}</b> / <b>{convert_size(disk.total)}</b>\n"
  sys_info_text += f"- Threads used: <b>{process.num_threads()}</b>\n"
  sys_info_text += f"- Created: <b>{datetime.datetime.fromtimestamp(int(process.create_time()))}</b>\n"

  await update.message.reply_text(sys_info_text)

@only_sys
async def sys_handle_db_conn_pool_info(update: Update, context: Context) -> None:
  assert update.message

  pool_stats = get_pool_stats()

  sys_info_text = ""
  sys_info_text += "<b>Database Connection Pool Stats Info:</b>\n"
  sys_info_text += f"- Requests number: <b>{pool_stats['requests_num']}</b>\n"
  sys_info_text += f"- Requests queued: <b>{pool_stats['requests_queued']}</b>\n"
  sys_info_text += f"- Connections: <b>{pool_stats['connections_ms']}ms</b>\n"
  sys_info_text += f"- Requests wait: <b>{pool_stats['requests_wait_ms']}ms</b>\n"
  sys_info_text += f"- Usage: <b>{pool_stats['usage_ms']}ms</b>\n"
  sys_info_text += f"- Pool size: <b>{pool_stats['pool_size']}</b> (min: <b>{pool_stats['pool_min']}</b>, max: <b>{pool_stats['pool_max']}</b>)\n"
  sys_info_text += f"- Pool available: <b>{pool_stats['pool_available']}</b>\n"
  sys_info_text += f"- Requests waiting: <b>{pool_stats['requests_waiting']}</b>\n"

  await update.message.reply_text(sys_info_text)

@only_sys
async def sys_handle_db_stat_activity_info(update: Update, context: Context) -> None:
  assert update.message

  stats = await Sys.get_database_stat_activity()

  sys_db_stat_activity_info_text = ""
  sys_db_stat_activity_info_text += "<b>Database Stat Activity Info:</b>\n\n"

  for stat in stats:
    sys_db_stat_activity_info_text += f"<b>PID</b>: {stat.pid}, <b>IP</b>: {stat.client_addr}, <b>State:</b> {stat.state}\n"
    sys_db_stat_activity_info_text += f"<b>Date</b>: {stat.query_start}\n"
    sys_db_stat_activity_info_text += f"<b>Query</b>: <code>{stat.query[:80]}...</code>\n\n"

  await update.message.reply_text(sys_db_stat_activity_info_text)

async def _sys_backup_func(context: Context, chat_id: int):
  accounts_backup_file_path = await Sys.backup_accounts()
  await context.bot.send_document(chat_id, accounts_backup_file_path)
  pathlib.Path(accounts_backup_file_path).unlink(missing_ok=True)

  groups_backup_file_path = await Sys.backup_groups()
  await context.bot.send_document(chat_id, groups_backup_file_path)
  pathlib.Path(groups_backup_file_path).unlink(missing_ok=True)

@only_sys
async def sys_handle_backup(update: Update, context: Context) -> None:
  assert update.message and update.effective_message and update.effective_chat and context.job_queue

  await update.effective_message.reply_text("Backup job scheduled.")

  context.job_queue.run_once(lambda x: _sys_backup_func(x, update.effective_chat.id), 1)

@only_sys
async def sys_handle_sync_commands(update: Update, context: Context) -> None:
  assert update.message and update.effective_message

  await Command.sync_commands(context.instance.id, context.bot)

  await update.effective_message.reply_text("Commands are synced.")

# @only_sys
# async def sys_handle_reset_webhook(update: Update, context: Context) -> None:
#   assert update.message and update.effective_message and update.effective_chat
# 
#   await context.bot.delete_webhook(True)
#   webhook_url = WEBHOOK_URL.format(context.instance.id)
#   await context.bot.set_webhook(webhook_url, allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
# 
#   await update.effective_message.reply_text("Webhook is reset")

@only_sys
async def sys_handle_pending_updates(update: Update, context: Context) -> None:
  assert update.message and update.effective_message and update.effective_chat

  pending_updates = context.application.update_queue.qsize()

  await update.message.reply_text(f"Pending updates: {pending_updates}")

@only_sys
async def sys_handle_reset_pending_updates(update: Update, context: Context) -> None:
  assert update.effective_message

  update_queue = context.application.update_queue

  while not update_queue.empty():
    update_queue.get_nowait()
    update_queue.task_done()

  await update.effective_message.reply_text("Pending updates are reset.")

@only_sys
async def sys_handle_toggle_feature(update: Update, context: Context):
  assert update.effective_message

  if len(context.args) < 2 or context.args[1] not in ["on", "off"]:
    await update.effective_message.reply_text("Invalid arguments")
    return

  try:
    if context.args[1] == "on":
      await Instance.enable_feature(context.instance.id, context.args[0])
    else:
      await Instance.disable_feature(context.instance.id, context.args[0])
  except:
    await update.effective_message.reply_text("Unable to toggle the feature")
    return

  await update.effective_message.reply_text("Success")

@only_sys
async def sys_handle_bootstrap(update: Update, context: Context):
  assert update.effective_message

  context.bot_data["bootstrap"] = True

  await update.effective_message.reply_text("Success")


def _to_status_emoji(enabled: bool):
  return f"{'✅' if enabled else '🚫'}"

def _to_status_text(enabled: bool):
  return f"{'on' if enabled else 'off'}"

async def _features(context: Context):
  features_text = "Features:"

  reply_markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(f"⚙️ Track search feature: {_to_status_emoji(context.instance.track_search_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_SEARCH.value}_{_to_status_text(not context.instance.track_search_feature_enabled)}"),],
    [InlineKeyboardButton(f"⚙️ Track download feature: {_to_status_emoji(context.instance.track_download_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_DOWNLOAD.value}_{_to_status_text(not context.instance.track_download_feature_enabled)}"),],
    [InlineKeyboardButton(f"⚙️ Track recognize from voice feature: {_to_status_emoji(context.instance.track_recognize_from_voice_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_RECOGNIZE_FROM_VOICE.value}_{_to_status_text(not context.instance.track_recognize_from_voice_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Track recognize from audio feature: {_to_status_emoji(context.instance.track_recognize_from_audio_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_RECOGNIZE_FROM_AUDIO.value}_{_to_status_text(not context.instance.track_recognize_from_audio_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Track recognize from video note feature: {_to_status_emoji(context.instance.track_recognize_from_video_note_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO_NOTE.value}_{_to_status_text(not context.instance.track_recognize_from_video_note_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Track recognize from video feature: {_to_status_emoji(context.instance.track_recognize_from_video_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TRACK_RECOGNIZE_FROM_VIDEO.value}_{_to_status_text(not context.instance.track_recognize_from_video_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ Instagram feature: {_to_status_emoji(context.instance.instagram_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.INSTAGRAM.value}_{_to_status_text(not context.instance.instagram_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Instagram recognize track feature: {_to_status_emoji(context.instance.instagram_recognize_track_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.INSTAGRAM_RECOGNIZE_TRACK.value}_{_to_status_text(not context.instance.instagram_recognize_track_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ Tiktok feature: {_to_status_emoji(context.instance.tiktok_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TIKTOK.value}_{_to_status_text(not context.instance.tiktok_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Tiktok recognize track feature: {_to_status_emoji(context.instance.tiktok_recognize_track_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TIKTOK_RECOGNIZE_TRACK.value}_{_to_status_text(not context.instance.tiktok_recognize_track_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ Twitter feature: {_to_status_emoji(context.instance.twitter_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TWITTER.value}_{_to_status_text(not context.instance.twitter_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Likee feature: {_to_status_emoji(context.instance.likee_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.LIKEE.value}_{_to_status_text(not context.instance.likee_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Tumblr feature: {_to_status_emoji(context.instance.tumblr_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.TUMBLR.value}_{_to_status_text(not context.instance.tumblr_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Pinterest feature: {_to_status_emoji(context.instance.pinterest_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.PINTEREST.value}_{_to_status_text(not context.instance.pinterest_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Facebook feature: {_to_status_emoji(context.instance.facebook_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.FACEBOOK.value}_{_to_status_text(not context.instance.facebook_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ YouTube search feature: {_to_status_emoji(context.instance.youtube_search_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.YOUTUBE_SEARCH.value}_{_to_status_text(not context.instance.youtube_search_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ YouTube download feature: {_to_status_emoji(context.instance.youtube_download_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.YOUTUBE_DOWNLOAD.value}_{_to_status_text(not context.instance.youtube_download_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ YouTube link feature: {_to_status_emoji(context.instance.youtube_link_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.YOUTUBE_LINK.value}_{_to_status_text(not context.instance.youtube_link_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ YouTube recognize track feature: {_to_status_emoji(context.instance.youtube_recognize_track_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.YOUTUBE_RECOGNIZE_TRACK.value}_{_to_status_text(not context.instance.youtube_recognize_track_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ Advertisement feature: {_to_status_emoji(context.instance.advertisement_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.ADVERTISEMENT.value}_{_to_status_text(not context.instance.advertisement_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Broadcast feature: {_to_status_emoji(context.instance.broadcast_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.BROADCAST.value}_{_to_status_text(not context.instance.broadcast_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Command feature: {_to_status_emoji(context.instance.command_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.COMMAND.value}_{_to_status_text(not context.instance.command_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Required join feature: {_to_status_emoji(context.instance.required_join_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.REQUIRED_JOIN.value}_{_to_status_text(not context.instance.required_join_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Join request feature: {_to_status_emoji(context.instance.join_request_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.JOIN_REQUEST.value}_{_to_status_text(not context.instance.join_request_feature_enabled)}")],
    [InlineKeyboardButton(f"⚙️ Referral feature: {_to_status_emoji(context.instance.referral_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.REFERRAL.value}_{_to_status_text(not context.instance.referral_feature_enabled)}")],

    [InlineKeyboardButton(f"⚙️ WEB feature: {_to_status_emoji(context.instance.web_feature_enabled)}", callback_data=f"sys_feature_{InstanceFeatures.WEB.value}_{_to_status_text(not context.instance.web_feature_enabled)}")],

    [InlineKeyboardButton(f"✅ SAVE CHANGES", callback_data="sys_bootstrap")],
  ])

  return (features_text, reply_markup,)

@only_sys
async def sys_handle_feature_toggle_callback_query(update: Update, context: Context):
  assert update.callback_query

  await update.callback_query.answer()

  feature = typing.cast(str, context.matches[0].group(1))
  is_enabled = True if context.matches[0].group(2) == "on" else False

  if is_enabled:
    await Instance.enable_feature(context.instance.id, feature)
  else:
    await Instance.disable_feature(context.instance.id, feature)

  context.instance = await Instance.get(context.instance.id)

  (features_text, reply_markup) = await _features(context)
  await update.callback_query.edit_message_text(features_text, reply_markup=reply_markup)

@only_sys
async def sys_handle_bootstrap_callback_query(update: Update, context: Context):
  assert update.callback_query

  context.bot_data["bootstrap"] = True

  await update.callback_query.answer("Chanages applied")

  await update.callback_query.delete_message()

@only_sys
async def sys_handle_features_command(update: Update, context: Context):
  assert update.effective_message

  (features_text, reply_markup) = await _features(context)

  await update.effective_message.reply_text(features_text, reply_markup=reply_markup)