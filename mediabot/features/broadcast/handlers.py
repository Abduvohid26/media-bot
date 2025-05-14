import asyncio
import typing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, \
    Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler, Application
from telegram.error import BadRequest, Forbidden
from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.account.model import Account
from mediabot.features.group.model import Group
from mediabot.features.broadcast.model import BROADCAST_ACCOUNT_COUNT_PER_ITER, BROADCAST_GROUP_COUNT_PER_ITER, \
    BROADCAST_STATE_CREATE_IS_GROUP, BROADCAST_STATE_CREATE_IS_SILENT, BROADCAST_STATE_CREATE_JOBS, \
    BROADCAST_STATE_CREATE_LANGUAGE, BROADCAST_STATE_CREATE_MESSAGE, BROADCAST_STATE_CREATE_NAME, _Broadcast, Broadcast
from mediabot.features.message.model import Message as MessageModel
from mediabot.features.language.model import Language
from mediabot.features.account.model import ACCOUNT_SYS_ID_LIST
from mediabot.features.instance.model import Instance, _Instance

async def _broadcast(broadcast_id: int) -> typing.Union[str, InlineKeyboardMarkup]:
  broadcast = await Broadcast.get(broadcast_id)
  assert broadcast, f"broadcast does not exist ({broadcast_id})"

  broadcast_text = ""

  status = "▶️ Running" if broadcast.is_running else "⏸ Pause"
  silent = "🔕" if broadcast.is_silent else "🔔"
  group = "👥" if broadcast.is_group else "👤"

  completed_jobs = broadcast.succeeded_jobs + broadcast.blocked_jobs + broadcast.failed_jobs
  completed_percentage = "{:.2f}".format((completed_jobs / (broadcast.jobs or 1)) * 100)

  broadcast_text += f"{broadcast.id}) {broadcast.name} [{completed_jobs:,}/{broadcast.jobs:,} ~{completed_percentage}%] [{silent} {group}]\n"
  broadcast_text += f"<b>Status:</b> {status}\n"
  broadcast_text += f"<b>Language:</b> {broadcast.message.language.name if broadcast.message.language else '-'}\n"
  broadcast_text += f"<b>Cursor:</b> {broadcast.cursor or '-'}\n"
  broadcast_text += f"<b>Created at:</b> {broadcast.created_at}\n"
  broadcast_text += "------------------------------------------------------"

  inline_buttons = [
    [
      InlineKeyboardButton(f"Status: {'▶ Running' if broadcast.is_running else '⏸ Pause'}", callback_data=f"broadcast_status_toggle_{broadcast.id}"),
      InlineKeyboardButton(f"📩 Show message", callback_data=f"broadcast_message_show_{broadcast.message.id}")
    ],
    [
      InlineKeyboardButton(f"🗑 Delete", callback_data=f"broadcast_delete_{broadcast.id}"),
      InlineKeyboardButton(f"🔄 Refresh", callback_data=f"broadcast_{broadcast.id}"),
    ],
    [
      InlineKeyboardButton(f"⬅ Back", callback_data="broadcast")
    ]
  ]

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (broadcast_text, reply_markup,)

@only_admin
async def broadcast_handle_create_callback_query(update: Update, context: Context) -> object:
  assert update.effective_message

  await update.callback_query.answer()

  await update.effective_message.reply_text("Broadcast name:")

  return BROADCAST_STATE_CREATE_NAME

@only_admin
async def broadcast_handle_create_name(update: Update, context: Context) -> object:
  assert update.message and context.user_data is not None

  context.user_data.setdefault("broadcast_create_name", update.message.text)
  await update.message.reply_text("Please send/forward the message:")

  return BROADCAST_STATE_CREATE_MESSAGE

@only_admin
async def broadcast_handle_create_message(update: Update, context: Context) -> object:
  assert update.message and context.user_data is not None

  context.user_data.setdefault("broadcast_create_message", update.message.to_json())

  instance = context.instance
  languages = await Language.get_all(instance.id)

  keyboard_buttons = [
    [KeyboardButton(languages[outer*3+inner].name) for inner in range(min(3, len(languages) - (outer*3)))] for outer in range(max(len(languages), round(len(languages) / 3)))
  ]

  keyboard_buttons.append([KeyboardButton("❌")])

  reply_markup = ReplyKeyboardMarkup(keyboard_buttons)
  await update.message.reply_text("Please select broadcast message language", reply_markup=reply_markup)

  return BROADCAST_STATE_CREATE_LANGUAGE

@only_admin
async def broadcast_handle_create_message_language(update: Update, context: Context) -> typing.Union[object, None]:
  assert update.message and context.user_data is not None

  instance = context.instance
  languages = await Language.get_all(instance.id)
  language_origin = None

  if update.message.text != "❌":
    target_languages = [language for language in languages if language.name == update.message.text]
    if not target_languages:
      await update.message.reply_text("Invalid language")
      return

    language_origin = target_languages[0].id

  context.user_data.setdefault("broadcast_create_language_origin", language_origin)

  reply_markup = ReplyKeyboardRemove()
  await update.message.reply_text("Please select jobs count:", reply_markup=reply_markup)

  return BROADCAST_STATE_CREATE_JOBS

@only_admin
async def broadcast_handle_create_jobs(update: Update, context: Context) -> typing.Union[object, None]:
  assert update.message and update.message.text and context.user_data is not None

  if not update.message.text.isnumeric():
    await update.message.reply_text("Invalid number, please try again")
    return

  context.user_data.setdefault("broadcast_create_jobs", int(update.message.text))

  keyboard_buttons = [[KeyboardButton("Yes"), KeyboardButton("No")]]
  reply_markup = ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True)

  await update.message.reply_text("Is this for groups?", reply_markup=reply_markup)

  return BROADCAST_STATE_CREATE_IS_GROUP

@only_admin
async def broadcast_handle_create_is_group(update: Update, context: Context) -> typing.Union[object, None]:
  assert update.message and update.message.text and context.user_data is not None

  is_group = True if update.message.text == "Yes" else False
  context.user_data.setdefault("broadcast_create_is_group", is_group)

  keyboard_buttons = [[KeyboardButton("Yes"), KeyboardButton("No")]]
  reply_markup = ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True)

  await update.message.reply_text("Send messages silently?", reply_markup=reply_markup)

  return BROADCAST_STATE_CREATE_IS_SILENT

@only_admin
async def broadcast_handle_create_is_silent(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message and update.message.text and context.user_data is not None

  is_group = True if update.message.text == "Yes" else False
  context.user_data.setdefault("broadcast_create_is_silent", is_group)

  instance = context.instance
  name = context.user_data.pop("broadcast_create_name")
  message = context.user_data.pop("broadcast_create_message")
  language_origin = context.user_data.pop("broadcast_create_language_origin")
  is_silent = True if update.message.text == "Yes" else False
  is_group = context.user_data.pop("broadcast_create_is_group")
  jobs = context.user_data.pop("broadcast_create_jobs")

  created_broadcast_id = await Broadcast.create(instance.id, name, message, jobs, is_group, is_silent, language_origin)

  (broadcast_text, broadcast_reply_markup) = await _broadcast(created_broadcast_id)
  await update.message.reply_text(broadcast_text, reply_markup=broadcast_reply_markup)

  return ConversationHandler.END

@only_admin
async def broadcast_handle_broadcasts_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  instance = context.instance
  broadcasts = await Broadcast.get_all(instance.id)
  broadcasts_text = f"📯️ <b>Broadcasts</b>:\n\n"

  for broadcast_index, broadcast in enumerate(broadcasts):
    status = "▶️ Running" if broadcast.is_running else "⏸ Pause"
    silent = "🔕" if broadcast.is_silent else "🔔"
    group = "👥" if broadcast.is_group else "👤"

    completed_jobs = broadcast.succeeded_jobs + broadcast.blocked_jobs + broadcast.failed_jobs
    completed_percentage = "{:.2f}".format((completed_jobs / (broadcast.jobs or 1)) * 100)

    broadcasts_text += f"{broadcast_index+1}) {broadcast.name} [{completed_jobs:,}/{broadcast.jobs:,}~{completed_percentage}%] [{silent} {group}]\n"
    broadcasts_text += f"<b>Status:</b> {status}\n"
    broadcasts_text += f"<b>Language:</b> {broadcast.message.language.name if broadcast.message.language else '-'}\n"
    broadcasts_text += f"<b>Created at:</b> {broadcast.created_at}\n\n"

  inline_buttons = [
    [InlineKeyboardButton("✏️ " + str(outer*4+inner+1), callback_data=f"broadcast_{broadcasts[outer*4+inner].id}")
      for inner in range(min(4, len(broadcasts) - (outer*4)))] for outer in range(max(len(broadcasts), round(len(broadcasts) / 4)))
  ]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="broadcast_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  await update.callback_query.edit_message_text(broadcasts_text, reply_markup=reply_markup)

@only_admin
async def broadcast_handle_broadcast_callback_query(update: Update, context: Context, broadcast_id: typing.Union[int, None] = None) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  broadcast_id = broadcast_id or int(context.matches[0].groups(0)[0])

  (broadcast_text, reply_markup,) = await _broadcast(broadcast_id)

  await update.callback_query.edit_message_text(broadcast_text, reply_markup=reply_markup)

@only_admin
async def broadcast_handle_delete_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  broadcast_id = int(context.matches[0].groups(0)[0])
  await Broadcast.delete(broadcast_id)

  await broadcast_handle_broadcasts_callback_query(update, context)

@only_admin
async def broadcast_handle_message_show_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and update.callback_query.message and context.matches
  
  await update.callback_query.answer()

  message_id = int(context.matches[0].groups(0)[0])
  message = await MessageModel.get(message_id)
  assert message

  target_message_to_send = Message.de_json(message.message, context.bot)
  if not target_message_to_send:
    return

  await MessageModel.send_from_message(update.callback_query.message.chat.id, target_message_to_send, context.bot)

async def _broadcast_message_send(context: Context, chat_id: int, message: dict):
  try:
    async with context.batch_limiter:
      sent_message = await MessageModel.send_from_message(chat_id, Message.de_json(message, context.bot), context.bot)
      return (chat_id, sent_message,)
  except (BadRequest, Forbidden) as ex:
    if ex.message in ["Bad request: user not found",
                      "Forbidden: user is deactivated",
                      "Forbidden: bot was blocked by the user",
                      "Forbidden: bot was kicked from the supergroup chat",
                      "Forbidden: bot was kicked from the group chat",
                      "Bad Request: chat not found"]:
      return (chat_id, False,)
  except Exception as ex:
    pass

  return (chat_id, None,)

async def _broadcast_notify_admins(context: Context, instance_id: int, broadcast: _Broadcast):
  instance_admin_telegram_id_all = (await Account.get_admin_id_all(instance_id)) + ACCOUNT_SYS_ID_LIST

  message_content = f"📯️ Broadcast: <b>{broadcast.name}</b> has finished. Succeeded jobs: <b>{broadcast.succeeded_jobs:,}</b>, failed jobs: <b>{broadcast.failed_jobs:,}</b>, blocked jobs: <b>{broadcast.blocked_jobs:,}</b>"
  reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("View", callback_data=f"broadcast_{broadcast.id}")]])

  for instance_admin_telegram_id in instance_admin_telegram_id_all:

    try:
      await context.bot.send_message(instance_admin_telegram_id, message_content, reply_markup=reply_markup)
    except:
      pass

async def _broadcast_account_job_iter_run(context: Context):
  assert context.job and context.job_queue

  broadcast_id = typing.cast(int, context.job.data["broadcast_id"])
  instance = typing.cast(_Instance, context.job.data["instance"])

  broadcast = await Broadcast.get(broadcast_id)

  if not broadcast or not broadcast.is_running or broadcast.is_group:
    return

  if (broadcast.succeeded_jobs + broadcast.failed_jobs + broadcast.blocked_jobs) >= broadcast.jobs:
    await Broadcast.set_is_running(broadcast_id, False)
    await _broadcast_notify_admins(context, instance.id, broadcast)
    return

  broadcast_message_language_origin = broadcast.message.language.id \
      if broadcast.message.language else None

  account_list = await Account.get_many_for_broadcast(instance.id, broadcast.cursor, broadcast_message_language_origin, BROADCAST_ACCOUNT_COUNT_PER_ITER)
  if not account_list:
    await Broadcast.set_is_running(broadcast_id, False)
    await _broadcast_notify_admins(context, instance.id, broadcast)
    return

  broadcast_message_results = await asyncio.gather(*[_broadcast_message_send(context, account.telegram_id, \
      broadcast.message.message) for account in account_list])

  succeeded_results = [result for result in broadcast_message_results if isinstance(result[1], Message)]
  failed_results = [result for result in broadcast_message_results if result[1] is None]
  blocked_results = [result for result in broadcast_message_results if result[1] is False]

  max_account = max(account_list, key=lambda account: account.id)

  await Broadcast.update_state(broadcast_id, max_account.id, len(succeeded_results), len(failed_results), len(blocked_results))

  if blocked_results:
    await Account.set_deleted_at_many(instance.id, list(map(lambda result: result[0], blocked_results)))

  context.job_queue.run_once(_broadcast_account_job_iter_run, 1, name=context.job.name, data=context.job.data)

async def _broadcast_group_job_iter_run(context: Context):
  assert context.job and context.job_queue

  broadcast_id = typing.cast(int, context.job.data["broadcast_id"])
  instance = typing.cast(_Instance, context.job.data["instance"])

  broadcast = await Broadcast.get(broadcast_id)

  if not broadcast or not broadcast.is_running or not broadcast.is_group:
    return

  if (broadcast.succeeded_jobs + broadcast.failed_jobs + broadcast.blocked_jobs) >= broadcast.jobs:
    await Broadcast.set_is_running(broadcast_id, False)
    await _broadcast_notify_admins(context, instance.id, broadcast)
    return

  group_list = await Group.get_many_for_broadcast(instance.id, broadcast.cursor, BROADCAST_GROUP_COUNT_PER_ITER)
  if not group_list:
    await Broadcast.set_is_running(broadcast_id, False)
    await _broadcast_notify_admins(context, instance.id, broadcast)
    return

  broadcast_message_results = await asyncio.gather(*[_broadcast_message_send(context, group.group_id, \
      broadcast.message.message) for group in group_list])

  succeeded_results = [result for result in broadcast_message_results if isinstance(result[1], Message)]
  failed_results = [result for result in broadcast_message_results if result[1] is None]
  blocked_results = [result for result in broadcast_message_results if result[1] is False]

  max_group = max(group_list, key=lambda group: group.id)

  await Broadcast.update_state(broadcast_id, max_group.id, len(succeeded_results), len(failed_results), len(blocked_results))

  if blocked_results:
    await Group.set_deleted_at_many(instance.id, list(map(lambda result: result[0], blocked_results)))

  context.job_queue.run_once(_broadcast_group_job_iter_run, 1, name=context.job.name, data=context.job.data)

@only_admin
async def broadcast_handle_status_toggle_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and context.job_queue

  await update.callback_query.answer()

  broadcast_id = int(context.matches[0].groups(0)[0])
  broadcast = await Broadcast.get(broadcast_id)

  assert broadcast, f"broadcast does not exist ({broadcast_id})"

  if broadcast.is_running:
    await Broadcast.set_is_running(broadcast_id, False)
    return

  await _broadcast_run(context.application, context.instance, broadcast)

async def _broadcast_run(botapp: Application, instance: Instance, broadcast: _Broadcast):
  job_name = f"broadcast:job:{instance.id}:{broadcast.id}"

  already_running_job = botapp.job_queue.get_jobs_by_name(job_name)
  if already_running_job:
    return

  job_data = {"broadcast_id": broadcast.id, "instance": instance}
  await Broadcast.set_is_running(broadcast.id, True)

  if broadcast.is_group:
    botapp.job_queue.run_once(_broadcast_group_job_iter_run, 1, name=job_name, data=job_data)
  else:
    botapp.job_queue.run_once(_broadcast_account_job_iter_run, 1, name=job_name, data=job_data)

async def broadcast_run_running_broadcasts(instance_origin: int, botapp: Application, instance: Instance):
  broadcasts = await Broadcast.get_all(instance_origin)

  for broadcast in broadcasts:
    if not broadcast.is_running:
      continue

    await _broadcast_run(botapp, instance, broadcast)
