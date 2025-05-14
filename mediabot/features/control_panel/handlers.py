import typing
import datetime

from telegram import Update
from telegram.ext import ApplicationHandlerStop
from telegram.constants import BotNameLimit

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.control_panel.buttons import ControlPanelKeyboardMarkup

from mediabot.features.advertisement.model import Advertisement
from mediabot.features.broadcast.model import Broadcast
from mediabot.features.account.model import Account
from mediabot.features.group.model import Group
from mediabot.features.command.model import Command
from mediabot.features.referral.model import Referral
from mediabot.features.language.model import Language
from mediabot.features.required_join.model import RequiredJoin
from mediabot.features.join_request.model import JoinRequest
from mediabot.features.instance.model import Instance as InstanceModel

def _format_quota(quota: int) -> str:
  return "∞" if quota == -1 else f"{quota:,}"

def _format_growth_percentage(percentage: int):
  if percentage == 0:
    return f"= {percentage:.2f}%"

  return f"↑ +{percentage:.2f}%" if percentage >= 0 else f"↓ {percentage:.2f}%"

async def _control_panel(context: Context):
  advertisement_count = await Advertisement.count(context.instance.id)
  broadcast_count = await Broadcast.count(context.instance.id)
  command_count = await Command.count(context.instance.id)
  language_count = await Language.count(context.instance.id)
  required_join_count = await RequiredJoin.count(context.instance.id)
  referral_count = await Referral.count(context.instance.id)
  join_request_chat_count = await JoinRequest.chat_count(context.instance.id)

  control_panel_text = """
    Welcome to the control panel!\n
<b>Commands</b>:
/set_admin - Set account as admin (<code>/set_admin 12345</code>)
/unset_admin - Unset account as admin (<code>/unset_admin 12345</code>)
/set_bot_name - Set bot name (<code>/set_bot_name en MYBOT</code> or <code>/set_bot_name all MYBOT</code>)
  """

  control_panel_reply_markup = ControlPanelKeyboardMarkup.build(advertisement_count, broadcast_count, \
      command_count, language_count, required_join_count, referral_count, join_request_chat_count)

  return (control_panel_text, control_panel_reply_markup,)

@only_admin
async def control_panel_handle_control_panel_command(update: Update, context: Context):
  assert update.effective_message

  (text, reply_markup) = await _control_panel(context)

  await update.effective_message.reply_text(text, reply_markup=reply_markup)

@only_admin
async def control_panel_handle_control_panel_callback_query(update: Update, context: Context):
  assert update.callback_query

  (text, reply_markup) = await _control_panel(context)

  await update.effective_message.edit_text(text, reply_markup=reply_markup)

@only_admin
async def control_panel_handle_set_bot_name_command(update: Update, context: Context):
  assert update.message and context.args and len(context.args) == 2

  language_code = context.args[0]
  name = context.args[1]

  if len(name) > BotNameLimit.MAX_NAME_LENGTH:
    return await update.message.reply_text(f"Invalid length, must be <= {BotNameLimit.MAX_NAME_LENGTH}")

  # TODO(mhw0): this method is failing if name has many characters
  await context.bot.set_my_name(name, None if language_code == "all" or len(language_code) > 2 else language_code)

  await update.message.reply_text("Success")

  raise ApplicationHandlerStop()

@only_admin
async def control_panel_handle_set_admin_command(update: Update, context: Context):
  assert update.message and context.args and len(context.args) == 1 and context.args[0].isnumeric()

  await Account.set_is_admin(context.instance.id, int(context.args[0]), True)

  await update.message.reply_text("Success")

  raise ApplicationHandlerStop()

@only_admin
async def control_panel_handle_unset_admin_command(update: Update, context: Context):
  assert update.message and context.args and len(context.args) == 1 and context.args[0].isnumeric()

  await Account.set_is_admin(context.instance.id, int(context.args[0]), False)

  await update.message.reply_text("Success")

  raise ApplicationHandlerStop()

@only_admin
async def control_panel_handle_statistics_callback_query(update: Update, context: Context):
  assert update.effective_message

  statistics_text = f"<b>Statistics for</b>: {datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

  account_statistics = await Account.get_statistics(context.instance.id)
  account_statistics = sorted(account_statistics, key=lambda stat: stat.account_count, reverse=True)
  group_statistics = await Group.get_statistics(context.instance.id)

  total_account_count = sum(stat.account_count for stat in account_statistics)
  total_deleted_account_count = sum(stat.deleted_account_count for stat in account_statistics)
  total_today_new_account_count = sum(stat.today_new_account_count for stat in account_statistics)
  total_today_deleted_account_count = sum(stat.today_deleted_account_count for stat in account_statistics)

  statistics_text += "<b>Accounts</b>:\n"
  for statistics in account_statistics:
    statistics_text += f"- {statistics.language_name or '🏳️ Unknown'}: <b>+{statistics.account_count - statistics.deleted_account_count:,}</b> / -<b>{statistics.deleted_account_count:,}</b> (<b>+{statistics.today_new_account_count:,}</b> / <b>-{statistics.today_deleted_account_count:,}</b>)\n"

  statistics_text += f"= <b>+{total_account_count - total_deleted_account_count:,}</b> / <b>-{total_deleted_account_count:,}</b> (<b>+{total_today_new_account_count:,}</b> / <b>-{total_today_deleted_account_count:,}</b>)\n"

  statistics_text += "\n"

  statistics_text += "<b>Groups</b>:\n"

  statistics_text += f"<b>+{group_statistics.group_count - group_statistics.deleted_group_count:,}</b> / <b>-{group_statistics.deleted_group_count:,}</b> (<b>+{group_statistics.today_new_group_count}</b> / <b>-{group_statistics.today_deleted_group_count:,}</b>)\n"

  statistics_text += "\n"

  statistics_text += "<b>Resource usage</b>:\n"

  if context.instance.track_search_feature_enabled or context.instance.track_download_feature_enabled:
    statistics_text += f"- <b>Track:</b> {_format_quota(context.instance.track_used)} / {_format_quota(context.instance.track_quota)}\n"

  if context.instance.instagram_feature_enabled:
    statistics_text += f"- <b>Instagram:</b> {_format_quota(context.instance.instagram_used)} / {_format_quota(context.instance.instagram_quota)}\n"

  if context.instance.tiktok_feature_enabled:
    statistics_text += f"- <b>Tiktok:</b> {_format_quota(context.instance.tiktok_used)} / {_format_quota(context.instance.tiktok_quota)}\n"

  if context.instance.youtube_download_feature_enabled:
    statistics_text += f"- <b>YouTube:</b> {_format_quota(context.instance.youtube_used)} / {_format_quota(context.instance.youtube_quota)}\n"

  statistics_text += "\n"

  three_days_ago = datetime.datetime.today() - datetime.timedelta(days=3)
  [three_days_ago_request_mark_count, three_days_ago_unique_request_mark_count] = await InstanceModel.get_request_mark_count(context.instance.id, three_days_ago)

  two_days_ago = datetime.datetime.today() - datetime.timedelta(days=2)
  [two_days_ago_request_mark_count, two_days_ago_unique_request_mark_count] = await InstanceModel.get_request_mark_count(context.instance.id, two_days_ago)
  two_days_ago_growth_percentage = ((two_days_ago_request_mark_count - three_days_ago_request_mark_count) / (three_days_ago_request_mark_count or 1)) * 100

  yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
  [yesterday_request_mark_count, yesterday_unique_request_mark_count] = await InstanceModel.get_request_mark_count(context.instance.id, yesterday)
  yesterday_growth_percentage = ((yesterday_request_mark_count - two_days_ago_request_mark_count) / (two_days_ago_request_mark_count or 1)) * 100

  today = datetime.datetime.today()
  [today_request_mark_count, today_unique_request_mark_count] = await InstanceModel.get_request_mark_count(context.instance.id, today)
  today_growth_percentage = ((today_request_mark_count - yesterday_request_mark_count) / (yesterday_request_mark_count or 1)) * 100

  statistics_text += "<b>Activity</b>:\n"
  statistics_text += f"- 🗓 <b>{three_days_ago.strftime('%d.%m.%Y')}:</b> {three_days_ago_request_mark_count:,} (λ: {three_days_ago_unique_request_mark_count:,})\n"
  statistics_text += f"- 🗓 <b>{two_days_ago.strftime('%d.%m.%Y')}:</b> {two_days_ago_request_mark_count:,} (λ: {two_days_ago_unique_request_mark_count:,}) <b>{_format_growth_percentage(two_days_ago_growth_percentage)}</b>\n"
  statistics_text += f"- 🗓 <b>{yesterday.strftime('%d.%m.%Y')}:</b> {yesterday_request_mark_count:,} (λ: {yesterday_unique_request_mark_count:,}) <b>{_format_growth_percentage(yesterday_growth_percentage)}</b>\n"
  statistics_text += f"- 🗓 <b>{today.strftime('%d.%m.%Y')}:</b> {today_request_mark_count:,} (λ: {today_unique_request_mark_count:,}) <b>{_format_growth_percentage(today_growth_percentage)}</b>\n"
  statistics_text += f"- <b>Request rate:</b> {context.bot_instance.get_request_per_second()} r/s\n"

  statistics_text += "\n"

  statistics_text += "<b>Instance</b>:\n"
  statistics_text += f"- <b>Username:</b> @{context.instance.username}\n"
  statistics_text += f"- <b>Actions per second:</b> {_format_quota(context.instance.actions_per_second)}\n"
  statistics_text += f"- <b>Created at:</b> {context.instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

  await update.effective_message.reply_html(statistics_text)
