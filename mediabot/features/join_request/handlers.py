import random
import typing
import traceback
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.join_request.model import JOIN_REQUEST_STATE_CREATE, JoinRequest
from mediabot.features.message.model import Message as MessageModel
from mediabot.features.message.constants import MESSAGE_KIND_JOIN_REQUEST
import mediabot.features.account.handlers as account_feature_handlers

CANCEL_CHARACTER = "❌"
JOIN_REQUEST_CHAT_MAX_COUNT = 10

async def join_request_handle_chat_join_request(update: Update, context: Context):
  assert update.chat_join_request

  join_request_chat_chat = str(update.chat_join_request.chat.username or update.chat_join_request.chat.id)
  # TODO: this should also accept account_origin for internalization
  join_request_chat = await JoinRequest.get_chat_by_chat_for_join(context.instance.id, \
      join_request_chat_chat, update.effective_user.language_code)

  # if this chat does not exist in our chat list, just ignore it
  if not join_request_chat:
    context.logger.info(None, extra=dict(
      action="JOIN_REQUEST_UNKNOWN_CHAT",
      chat_id=join_request_chat_chat,
      user_id=update.chat_join_request.from_user.id
    ))
    return

  message_to_send = random.choice(join_request_chat.messages or [None]) 

  if join_request_chat.is_autoapprove:
    # TODO: log if we can't approve
    is_approved = await update.chat_join_request.approve()

    if is_approved:
      context.logger.info(None, extra=dict(
        action="JOIN_REQUEST_APPROVE",
        join_request_chat=join_request_chat_chat,
        user_id=update.chat_join_request.from_user.id
      ))

      if message_to_send:
        try:
          deserialized_message = Message.de_json(message_to_send, context.bot)
          assert deserialized_message, "unable to deserialize join request message"

          # send a message to the joined user
          await MessageModel.send_from_message(update.chat_join_request.from_user.id, deserialized_message, context.bot)

          # try to create a new account
          await account_feature_handlers.account_try_create(context, update.effective_chat.id, \
              update.effective_user.id, update.effective_user.language_code)
        except:
          context.logger.info(None, extra=dict(
            action="JOIN_REQUEST_MESSAGE_FAIL",
            join_request_chat=join_request_chat_chat,
            user_id=update.chat_join_request.from_user.id,
            stack_trace=traceback.format_exc()
          ))
  elif join_request_chat.is_autodecline:
    await update.chat_join_request.decline()

    context.logger.info(None, extra=dict(
      action="JOIN_REQUEST_DECLINE",
      join_request_chat=join_request_chat_chat,
      user_id=update.chat_join_request.from_user.id
    ))

    return

  # otherwise store the approval request in database
  await JoinRequest.create_join_request(context.instance.id, join_request_chat.id, \
      update.chat_join_request.from_user.id)

  context.logger.info(None, extra=dict(
    action="JOIN_REQUEST_CREATE",
    join_request_chat_id=join_request_chat.id,
    user_id=update.chat_join_request.from_user.id
  ))

async def _join_request_accept_or_decline(context: Context, chat_id: str, user_id: int, is_accept: bool):
  try:
    async with context.batch_limiter:
      if is_accept:
        await context.bot.approve_chat_join_request(chat_id, user_id)
        context.logger.info(None, extra=dict(
          action="JOIN_REQUEST_APPROVE",
          join_request_chat=chat_id,
          user_id=user_id
        ))
      else:
        await context.bot.decline_chat_join_request(chat_id, user_id)
        context.logger.info(None, extra=dict(
          action="JOIN_REQUEST_DECLINE",
          join_request_chat=chat_id,
          user_id=user_id
        ))
  except:
    context.logger.info(None, extra=dict(
      action="JOIN_REQUEST_FAIL",
      join_request_chat=chat_id,
      user_id=user_id,
      stack_trace=traceback.format_exc()
    ))

async def _join_request_iter_run(context: Context):
  assert context.job and context.job_queue

  join_request_chat_id = typing.cast(int, context.job.data["join_request_chat_id"])
  join_request_is_accept = typing.cast(bool, context.job.data["join_request_is_accept"])

  join_request_chat = await JoinRequest.get_chat(join_request_chat_id)
  if not join_request_chat:
    pass

  join_requests = await JoinRequest.get_join_request_by_cursor(join_request_chat_id, join_request_chat.cursor, 20)
  if not join_requests:
    return

  asyncio.gather(*[_join_request_accept_or_decline(context, join_request_chat.chat, \
      join_request.user_id, join_request_is_accept) for join_request in join_requests])

  max_join_request = max(join_requests, key=lambda join_request: join_request.id)

  await JoinRequest.update_cursor(join_request_chat.id, max_join_request.id)
  await JoinRequest.delete_many([join_request.id for join_request in join_requests])

  context.application.job_queue.run_once(_join_request_iter_run, 1, name=context.job.name, data=context.job.data)

async def _join_request_all_run(context: Context, join_request_chat_id: int, is_accept: bool):
  job_name = f"join_request:job:{context.instance.id}"
  job_data = {"join_request_chat_id": join_request_chat_id, "join_request_is_accept": is_accept}

  context.application.job_queue.run_once(_join_request_iter_run, 1, name=job_name, data=job_data)

async def _join_request_chat(join_request_chat_id: int) -> typing.Tuple[str, InlineKeyboardMarkup]:
  join_request_chat = await JoinRequest.get_chat(join_request_chat_id)
  assert join_request_chat, f"join request chat {join_request_chat_id} not found"

  join_request_chat_text = f"{join_request_chat.id}) <b>{join_request_chat.chat}</b>\n"
  join_request_chat_text += f"<b>Pending requests</b>: {join_request_chat.join_request_count:,}\n"
  join_request_chat_text += f"<b>Created at</b>: {join_request_chat.created_at}\n\n"

  inline_buttons = [
    [
      InlineKeyboardButton("✅ Accept all", callback_data=f"join_request_accept_{join_request_chat.id}"),
      InlineKeyboardButton("❌ Decline all", callback_data=f"join_request_decline_{join_request_chat.id}")
    ],
    [
      InlineKeyboardButton(f"⚙️ Auto approve: {'Yes' if join_request_chat.is_autoapprove else 'No'}", callback_data=f"join_request_toggle_is_autoapprove_{join_request_chat.id}_{int(join_request_chat.is_autoapprove)}"),
      InlineKeyboardButton(f"⚙️ Auto decline: {'Yes' if join_request_chat.is_autodecline else 'No'}", callback_data=f"join_request_toggle_is_autodecline_{join_request_chat.id}_{int(join_request_chat.is_autodecline)}")
    ],
    [
      InlineKeyboardButton(f"✉️ Messages ({join_request_chat.message_count})", callback_data=f"messages_{MESSAGE_KIND_JOIN_REQUEST}_{join_request_chat_id}"),
      InlineKeyboardButton("🔢 Reset", callback_data=f"join_request_reset_{join_request_chat.id}")
    ],
    [
      InlineKeyboardButton("◀ Back", callback_data="join_requests"),
      InlineKeyboardButton("🗑 Delete", callback_data=f"join_request_delete_{join_request_chat.id}")
    ]
  ]

  reply_markup = InlineKeyboardMarkup(inline_buttons)
  return (join_request_chat_text, reply_markup,)

@only_admin
async def join_request_handle_join_requests_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()

  join_request_chats = await JoinRequest.get_chats(context.instance.id)

  join_request_chats_text = f"<b>Join request chats</b>:\n\n"

  for join_request_chat in join_request_chats:
    join_request_chats_text += f"{join_request_chat.id}) <b>{join_request_chat.chat}</b>\n"
    join_request_chats_text += f"<b>Pending requests</b>: {join_request_chat.join_request_count:,}\n"
    join_request_chats_text += f"<b>Messages</b>: {join_request_chat.message_count:,}\n"
    join_request_chats_text += f"<b>Created at</b>: {join_request_chat.created_at}\n\n"

  inline_buttons = [
    [InlineKeyboardButton("✏️ " + str(join_request_chats[outer*4+inner].id), callback_data=f"join_request_{join_request_chats[outer*4+inner].id}")
      for inner in range(min(4, len(join_request_chats) - (outer*4)))] for outer in range(max(len(join_request_chats), round(len(join_request_chats) / 4)))
  ]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="join_request_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)
  await update.callback_query.edit_message_text(join_request_chats_text, reply_markup=reply_markup)

@only_admin
async def join_request_handle_toggle_is_autoapprove_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])
  is_autoapprove = bool(int(context.matches[0].groups(1)[1]))

  await JoinRequest.update_chat_is_autoapprove(join_request_chat_id, not is_autoapprove)

  await join_request_handle_join_request_callback_query(update, context)

@only_admin
async def join_request_handle_toggle_is_autodecline_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])
  is_autodecline = bool(int(context.matches[0].groups(1)[1]))

  await JoinRequest.update_chat_is_autodecline(join_request_chat_id, not is_autodecline)

  await join_request_handle_join_request_callback_query(update, context)

@only_admin
async def join_request_handle_join_request_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and context.user_data is not None

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])

  (join_request_chat_text, join_request_chat_reply_markup, ) = await _join_request_chat(join_request_chat_id)
  await update.callback_query.edit_message_text(join_request_chat_text, reply_markup=join_request_chat_reply_markup)

@only_admin
async def join_request_handle_reset_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])

  await JoinRequest.delete_join_requests(join_request_chat_id)
  await JoinRequest.update_cursor(join_request_chat_id, 0)

  (join_request_chat_text, join_request_chat_reply_markup) = await _join_request_chat(join_request_chat_id)
  await update.callback_query.edit_message_text(join_request_chat_text, reply_markup=join_request_chat_reply_markup)

@only_admin
async def join_request_handle_accept_callback_query(update: Update, context: Context) -> None:
  assert(update.callback_query and context.matches and isinstance(update.callback_query.message, Message))

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])

  await _join_request_all_run(context, join_request_chat_id, True)

@only_admin
async def join_request_handle_decline_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])

  await _join_request_all_run(context, join_request_chat_id, False)

@only_admin
async def join_request_handle_delete_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  join_request_chat_id = int(context.matches[0].groups(0)[0])

  await JoinRequest.delete_chat(join_request_chat_id)

  await join_request_handle_join_requests_callback_query(update, context)

@only_admin
async def join_request_handle_create_callback_query(update: Update, context: Context):
  assert update.effective_message

  join_request_chat_count = await JoinRequest.chat_count(context.instance.id)

  if join_request_chat_count >= JOIN_REQUEST_CHAT_MAX_COUNT:
    await update.callback_query.answer("⚠️ You reached max number of join request chats, please delete the old ones.", show_alert=True)
    return

  reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CANCEL_CHARACTER)]], one_time_keyboard=True)
  await update.effective_message.reply_text("Please enter chat username or id:", reply_markup=reply_markup)

  return JOIN_REQUEST_STATE_CREATE

@only_admin
async def join_request_handle_create_enter_message(update: Update, context: Context) -> int:
  assert update.effective_message

  if update.effective_message.text == CANCEL_CHARACTER:
    await update.effective_message.reply_text("Cancelled")
    return ConversationHandler.END

  created_join_request_chat_id = await JoinRequest.create_chat(context.instance.id, update.effective_message.text)

  (join_request_chat_text, join_request_chat_reply_markup, ) = await _join_request_chat(created_join_request_chat_id)
  await update.message.reply_text(join_request_chat_text, reply_markup=join_request_chat_reply_markup)

  return ConversationHandler.END
