import re
import typing
import random
import traceback
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message, ChatMember, Bot
from telegram.ext import ConversationHandler, ApplicationHandlerStop

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.message.model import Message as MessageModel
from mediabot.features.account.model import ACCOUNT_SYS_ID_LIST, Account
from mediabot.features.required_join.model import REQUIRED_JOIN_KINDS, REQUIRED_JOIN_STATE_CREATE_TARGET_CHAT, REQUIRED_JOIN_STATE_EDIT_END_TIME_ENTER, \
    REQUIRED_JOIN_STATE_EDIT_JOIN_LINK_ENTER, REQUIRED_JOIN_STATE_EDIT_SCHEDULE_COUNT_ENTER, REQUIRED_JOIN_STATE_EDIT_TARGET_CHAT_ENTER, \
    REQUIRED_JOIN_STATE_EDIT_TARGET_COUNT_ENTER, RequiredJoin, RequiredJoinKind, _RequiredJoinFor
from mediabot.utils import chunks
from mediabot.features.message.constants import MESSAGE_KIND_REQUIRED_JOIN

JOIN_LINK_REGEX = r"(?:t|telegram)\.(?:me|dog)/(joinchat/|\+)?([\w-]+)"
CHAT_REGEX = r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(\w{4,})$"
TELEGRAM_USERNAME_LINK_REGEX = r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(\w{4,})$"
TELEGRAM_INVITE_LINK_PATTERN = r"(?:@|(?:(?:(?:https?://)?t(?:elegram)?)\.me\/))(\+\w{16})"

async def _check_required_join(context: Context, required_join_id: int) -> bool:
  required_join = await RequiredJoin.get(required_join_id)

  if not required_join:
    return False

  # if the required join reached its target count, disable it and notify the admins
  if required_join.target_join_count and required_join.required_join_mark_has_joined_count >= required_join.target_join_count:
    await RequiredJoin.update_is_enabled(required_join_id, False)

    instance_admin_telegram_id_all = (await Account.get_admin_id_all(context.instance.id)) + ACCOUNT_SYS_ID_LIST
    reply_markup = InlineKeyboardMarkup([[
      InlineKeyboardButton("Show", callback_data=f"required_join_{required_join_id}")
    ]])
    message_content = f"🚪 Required join: <b>{required_join.target_chat}</b> has reached target join count. 👤 <b>{required_join.required_join_mark_has_joined_count:,}</b>, 👁 <b>{required_join.required_join_mark_count:,}</b>"

    for instance_admin_telegram_id in instance_admin_telegram_id_all:
      try:
        await context.bot.send_message(instance_admin_telegram_id, message_content, reply_markup=reply_markup)
      except:
        pass

    return False
  return True

async def chat_member_handle(update: Update, context: Context) -> None:
  assert update.chat_member

  # the bot can be added to any channels and thus the users who join to/left the channel may not be members of this bot
  if not context.account:
    return

  # try to find the required join by its target
  required_join = await RequiredJoin.get_for_join(context.instance.id, context.account.id, \
      update.chat_member.chat.username, update.chat_member.chat.id)

  # if there's no required join enabled for this chat, ignore it
  if not required_join:
    return

  can_next = await _check_required_join(context, required_join.id)
  if not can_next:
    return

  status_change = update.chat_member.difference().get("status")
  old_is_member, new_is_member = update.chat_member.difference().get("is_member", (None, None))

  # if status is the same, ignore
  if status_change is None:
    return

  old_status, new_status = status_change
  was_member = update.chat_member.old_chat_member.status \
    in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR] \
    or (old_status == ChatMember.RESTRICTED and old_is_member is True)

  is_member = update.chat_member.new_chat_member.status \
    in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR] \
    or (new_status == ChatMember.RESTRICTED and new_is_member is True)

  # if the account joined the chat
  if not was_member and is_member:
    await RequiredJoin.set_mark_has_joined(required_join.id, context.account.id, True)

    context.logger.info(None, extra=dict(
      action="REQUIRED_JOIN_JOIN",
      required_join_id=required_join.id,
      user_id=update.effective_user.id,
      chat_id=update.chat_member.chat.id
    ))

    after_join_messages = await RequiredJoin.get_after_join_messages_for(required_join.id, context.account.id)
    if after_join_messages:
      after_join_message = random.choice(after_join_messages)
      deserialized_after_join_message = Message.de_json(after_join_message.message, context.bot)

      assert deserialized_after_join_message, "unable to deserialize required join after join message"

      if after_join_message.is_forward:
        await deserialized_after_join_message.forward(update.effective_user.id)
      else:
        await MessageModel.send_from_message(update.effective_user.id, deserialized_after_join_message, context.bot)
    else:
      await context.bot.send_message(update.effective_user.id, "✅")

    # trigger other required joins
    await required_join_handle(context, update.chat_member.from_user.id, update.chat_member.from_user.id, required_join.kind)

    # trigger pending pending requests
    # for pending_request in context.get_pending_requests():
    #   if isinstance(pending_request, TrackSearchRequest):
    #     await track_handle_search_chat_member(update, context, pending_request.search_query)
    #   elif isinstance(pending_request, TrackDownloadRequest):
    #     await track_handle_download_chat_member(update, context, pending_request.track_id)
    #   elif isinstance(pending_request, YouTubeSearchRequest):
    #     await youtube_handle_search_chat_member(update, context, pending_request.search_query)
    #   elif isinstance(pending_request, YouTubeVideoDownloadRequest):
    #     await youtube_handle_video_download_chat_member(update, context, pending_request.video_id)
    #   elif isinstance(pending_request, YouTubeAudioDownloadRequest):
    #     await youtube_handle_audio_download_chat_member(update, context, pending_request.video_id)
    #   elif isinstance(pending_request, InstagramLinkRequest):
    #     await instagram_feature_handlers.instagram_handle_link_chat_member(update, context, pending_request.instagram_link)
    #   elif isinstance(pending_request, InstagramPlaylistItemDownloadRequest):
    #     await instagram_feature_handlers.instagram_handle_download_playlist_item_chat_member(update, context, pending_request.post_id, \
    #         pending_request.album_item, pending_request.advertisement_kind)
    #   elif isinstance(pending_request, TikTokLinkRequest):
    #     await tiktok_feature_handlers.tiktok_handle_link_chat_member(update, context, pending_request.tiktok_link)

    # cleanup the pending requests
    # context.clear_pending_requests()

  elif was_member and not is_member:
    context.logger.info(None, extra={
      "action": "REQUIRED_JOIN_LEFT",
      "required_join_id": required_join.id,
      "user_id": update.effective_user.id,
      "chat_id": update.chat_member.chat.id
    })

async def required_join_is_member(bot: Bot, account_telegram_id: int, required_join: _RequiredJoinFor) -> bool:
  if required_join.instance_id:
    target_account = await Account.get(required_join.instance_id, account_telegram_id)
    return target_account is not None
  else:
    target_chat_to_check = required_join.target_chat \
      if required_join.target_chat.lstrip("-").isnumeric() else "@" + required_join.target_chat

    chat_member = await bot.get_chat_member(target_chat_to_check, account_telegram_id)

    return chat_member.status in [ChatMember.OWNER, ChatMember.ADMINISTRATOR, \
        ChatMember.MEMBER, ChatMember.RESTRICTED]

async def required_join_handle(context: Context, chat_id: int, account_telegram_id: int, kind: RequiredJoinKind) -> None:
  account_language_origin = context.account.language.id if context.account.language else None
  required_joins = await RequiredJoin.get_all_for(context.instance.id, context.account.id, account_language_origin, kind)

  required_join_messages: list[dict] = []
  required_join_buttons: list[InlineKeyboardButton] = []

  for required_join in required_joins:
    can_next = await _check_required_join(context, required_join.id)
    if not can_next:
      return

    is_target_chat_member = False

    try:
      is_target_chat_member = await required_join_is_member(context.bot, account_telegram_id, required_join)
    except Exception:
      context.logger.error(None, extra=dict(
        action="REQUIRED_JOIN_CHAT_MEMBER_CHECK_FAILED",
        required_join_chat=required_join.target_chat,
        chat_id=chat_id,
        user_id=account_telegram_id,
        stack_trace=traceback.format_exc()
      ))
      continue

    # if the account hasn't seen the required join, create a "mark"
    if not required_join.has_mark:
      await RequiredJoin.create_mark(context.instance.id, required_join.id, context.account.id, is_target_chat_member)

    # if the has_joined is already set to true by chat member handler, go to the next one
    if is_target_chat_member and required_join.has_joined:
      continue

    # if the account is a member of the chat and the database has "has_joined" false, set it to true to synchronize
    if is_target_chat_member and not required_join.has_joined:
      await RequiredJoin.set_mark_has_joined(required_join.id, context.account.id, True)

    # if the account is a member, just go to the next required join check
    if is_target_chat_member:
      continue

    required_join_messages.extend(required_join.messages)

    join_link = required_join.join_link or ("https://t.me/" + required_join.target_chat.replace("@", ""))
    required_join_buttons.append(InlineKeyboardButton(context.l("required_join.default_button_text"), url=join_link))

  # if there's required joins to join
  if required_join_buttons:
    # build required join inline reply markup
    required_join_reply_markup = InlineKeyboardMarkup([[required_join_button] \
          for required_join_button in required_join_buttons])

    # if there are custom required join messages, pick random one and send it
    if required_join_messages:
      required_join_message = random.choice(required_join_messages)
      required_join_message["reply_markup"] = required_join_reply_markup.to_dict()
      deserialized_required_join_message = Message.de_json(required_join_message, context.bot)

      await MessageModel.send_from_message(chat_id, deserialized_required_join_message, context.bot)
      raise ApplicationHandlerStop()

    await context.bot.send_message(chat_id, context.l("required_join.default_text"), reply_markup=required_join_reply_markup)
    raise ApplicationHandlerStop()

@only_admin
async def required_join_handle_create_callback_query(update: Update, context: Context):
  assert update.effective_message

  await update.effective_message.reply_text("Please enter target chat to check (https://t.me/username or 12345678 id):")

  return REQUIRED_JOIN_STATE_CREATE_TARGET_CHAT

@only_admin
async def required_join_handle_create_target_chat_message(update: Update, context: Context):
  assert update.effective_message and update.effective_message.text

  username_link_matches = re.findall(TELEGRAM_USERNAME_LINK_REGEX, update.effective_message.text)
  # invite_link_matches = re.findall(TELEGRAM_INVITE_LINK_PATTERN, update.effective_message.text)

  # most likely that the message is chat id or username link
  if update.effective_message.text.lstrip("-").isdigit() or username_link_matches:
    target_chat = username_link_matches[0] if username_link_matches else update.effective_message.text
    created_required_join_id = await RequiredJoin.create(context.instance.id, target_chat)

    (required_join_text, required_join_reply_markup) = await _required_join(created_required_join_id)
    await update.effective_chat.send_message(required_join_text, reply_markup=required_join_reply_markup)

    return ConversationHandler.END

  await update.effective_message.reply_text("Invalid target chat to check, it should be either https://t.me/username or 12345678")

@only_admin
async def required_join_handle_create_cancel_message(update: Update, context: Context):
  assert update.effective_message

  await update.effective_message.reply_text("Cancelled")

  return ConversationHandler.END

async def _required_join_required_joins(context: Context):
  required_joins = await RequiredJoin.get_all(context.instance.id)

  required_joins_text = f"🚪 <b>Required joins</b>:\n\n"

  for index, required_join in enumerate(required_joins):
    join_percentage = (required_join.required_join_mark_has_joined_count / (required_join.target_join_count or 1)) * 100
    target = required_join.target_chat if required_join.target_chat.lstrip("-").isdigit() else "@" + required_join.target_chat
    is_optional_identifier = "?" if required_join.is_optional else "✓"
    required_joins_text += ("<s>" if not required_join.is_enabled else "") + f"<b>{index+1})</b> <b>{target}</b> (👤<b>{required_join.required_join_mark_has_joined_count:,}</b> / 👁<b>{required_join.required_join_mark_count:,}</b> / 🎯<b>{required_join.target_join_count:,}</b> ~<b>{join_percentage:.2f}%</b>) [{is_optional_identifier}]" + ("</s>" if not required_join.is_enabled else "") + "\n"
    required_joins_text += f"<b>⚙️ Kind</b>: <code>{required_join.kind}</code>\n"
    required_joins_text += f"<b>📎 Join link</b>: {required_join.join_link or '-'}\n"
    required_joins_text += f"<b>⏰ End time</b>: {required_join.target_end_time or '-'}\n"
    required_joins_text += f"<b>⏰ Created at</b>: {required_join.created_at}\n\n"

  inline_buttons = [[InlineKeyboardButton(f"✏️ {row_index*5+col_index+1}", callback_data=f"required_join_{required_join.id}")\
      for col_index, required_join in enumerate(row)] for row_index, row in enumerate(chunks(required_joins, 5))]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="required_join_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (required_joins_text, reply_markup,)

@only_admin
async def required_join_handle_required_joins_callback_query(update: Update, context: Context):
  assert update.callback_query and context.user_data is not None

  await update.callback_query.answer()

  (required_joins_text, reply_markup,) = await _required_join_required_joins(context)

  await update.callback_query.edit_message_text(required_joins_text, reply_markup=reply_markup)

@only_admin
async def required_join_handle_required_joins_message(update: Update, context: Context):
  assert update.message and context.user_data is not None and update.effective_message

  (required_joins_text, reply_markup,) = await _required_join_required_joins(context)

  await update.effective_message.reply_text(required_joins_text, reply_markup=reply_markup)

async def _required_join(required_join_id: int) -> typing.Union[str, InlineKeyboardMarkup]:
  required_join = await RequiredJoin.get(required_join_id)
  assert required_join, "required join does not exist"

  required_join_text = ""
  join_percentage = (required_join.required_join_mark_has_joined_count / (required_join.target_join_count or 1)) * 100
  target = required_join.target_chat if required_join.target_chat.lstrip("-").isdigit() else "@" + required_join.target_chat
  is_optional_identifier = "?" if required_join.is_optional else "✓"
  required_join_text += ("<s>" if not required_join.is_enabled else "") + f"<b>{required_join.id})</b> <b>{target}</b> (👤<b>{required_join.required_join_mark_has_joined_count:,}</b> / 👁<b>{required_join.required_join_mark_count:,}</b> / 🎯<b>{required_join.target_join_count:,}</b> ~<b>{join_percentage:.2f}%</b>) [{is_optional_identifier}]" + ("</s>" if not required_join.is_enabled else "") + "\n"
  required_join_text += f"<b>⚙️ Kind</b>: <code>{required_join.kind}</code>\n"
  required_join_text += f"<b>📎 Join link</b>: {required_join.join_link or '-'}\n"
  required_join_text += f"<b>⏰ End time</b>: {required_join.target_end_time or '-'}\n"
  required_join_text += f"<b>⏰ Created at</b>: {required_join.created_at}\n"
  required_join_text += f"--------------------------------------------------------\n\n"

  required_join_kind_index = REQUIRED_JOIN_KINDS.index(required_join.kind)

  required_join_buttons = [
    [
      InlineKeyboardButton(f"❔ Optional: {'Yes' if required_join.is_optional else 'No'}", callback_data=f"required_join_toggle_is_optional_{required_join.id}_{int(required_join.is_optional)}"),
      InlineKeyboardButton(f"Status: {'✅ Enabled' if required_join.is_enabled else '❌ Disabled'}", callback_data=f"required_join_toggle_is_enabled_{required_join.id}_{int(required_join.is_enabled)}"),
    ],
    [
      InlineKeyboardButton(f"🎯 Edit target join count", callback_data=f"required_join_edit_target_join_count_{required_join.id}"),
      InlineKeyboardButton(f"💬 Edit target chat", callback_data=f"required_join_edit_target_chat_{required_join.id}"),
    ],
    [
      InlineKeyboardButton(f"#️⃣ Edit schedule count", callback_data=f"required_join_edit_schedule_count_{required_join.id}"),
      InlineKeyboardButton(f"⏰ Edit end time", callback_data=f"required_join_edit_end_time_{required_join.id}"),
    ],
    [
      InlineKeyboardButton(f"🔗 Edit join link", callback_data=f"required_join_edit_join_link_{required_join.id}"),
      InlineKeyboardButton(f"⚙️ On: {required_join.kind}", callback_data=f"required_join_toggle_kind_{required_join.id}_{required_join_kind_index}"),
    ],
    [
      InlineKeyboardButton(f"✉️ Messages ({required_join.message_count})", callback_data=f"messages_{MESSAGE_KIND_REQUIRED_JOIN}_{required_join_id}"),
      InlineKeyboardButton(f"🗑 Delete", callback_data=f"required_join_delete_{required_join.id}"),
    ],
    [
      InlineKeyboardButton(f"⬅️ Back to required joins", callback_data=f"required_join"),
    ]
  ]

  required_join_reply_markup = InlineKeyboardMarkup(required_join_buttons)
  return (required_join_text, required_join_reply_markup,)

@only_admin
async def required_join_handle_required_join_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and context.user_data is not None

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  (required_join_text, required_join_reply_markup) = await _required_join(required_join_id)
  await update.callback_query.edit_message_text(required_join_text, reply_markup=required_join_reply_markup)

@only_admin
async def required_join_handle_delete_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  await RequiredJoin.delete(int(required_join_id))
  await required_join_handle_required_joins_callback_query(update, context)

@only_admin
async def required_join_handle_toggle_is_optional_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])
  is_optional = bool(int(context.matches[0].groups(1)[1]))

  await RequiredJoin.update_is_optional(required_join_id, not is_optional)

  await required_join_handle_required_join_callback_query(update, context)

@only_admin
async def required_join_handle_toggle_is_enabled_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])
  is_enabled = bool(int(context.matches[0].groups(1)[1]))

  await RequiredJoin.update_is_enabled(required_join_id, not is_enabled)

  await required_join_handle_required_join_callback_query(update, context)

@only_admin
async def required_join_handle_edit_target_join_count_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and context.user_data is not None and update.effective_message

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  await update.effective_message.reply_text("Please enter target join count:")

  context.user_data.setdefault("required_join_target_join_count_edit", int(required_join_id))

  return REQUIRED_JOIN_STATE_EDIT_TARGET_COUNT_ENTER

@only_admin
async def required_join_handle_edit_target_join_count_enter(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message and context.user_data is not None and update.message.text

  target_required_join_id = int(typing.cast(int, context.user_data.get("required_join_target_join_count_edit")))

  if not update.message.text.isnumeric():
    await update.message.reply_text("Invalid number")
    return

  target_join_count = int(update.message.text)
  await RequiredJoin.update_target_join_count(target_required_join_id, target_join_count)
  context.user_data.pop("required_join_target_join_count_edit")

  (required_join_text, reply_markup) = await _required_join(target_required_join_id)
  await update.effective_message.reply_text(required_join_text, reply_markup=reply_markup)

  return ConversationHandler.END

@only_admin
async def required_join_handle_edit_schedule_count_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and update.effective_message and context.user_data is not None

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])
  await update.effective_message.reply_text("Please enter schedule count:")

  context.user_data.setdefault("required_join_schedule_count_edit", int(required_join_id))

  return REQUIRED_JOIN_STATE_EDIT_SCHEDULE_COUNT_ENTER

@only_admin
async def required_join_handle_edit_schedule_count_enter(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message and context.user_data is not None and update.message.text

  target_required_join_id = int(typing.cast(int, context.user_data.get("required_join_schedule_count_edit")))

  if not update.message.text.isnumeric():
    await update.message.reply_text("Invalid number")
    return

  target_join_count = int(update.message.text)
  await RequiredJoin.update_schedule_count(target_required_join_id, target_join_count)
  context.user_data.pop("required_join_schedule_count_edit")

  (required_join_text, reply_markup) = await _required_join(target_required_join_id)
  await update.effective_message.reply_text(required_join_text, reply_markup=reply_markup)

  return ConversationHandler.END

@only_admin
async def required_join_handle_toggle_kind_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  required_join_id = int(context.matches[0].groups(0)[0])
  kind_index = int(context.matches[0].groups(1)[1])
  new_kind = REQUIRED_JOIN_KINDS[kind_index+1] \
    if kind_index < len(REQUIRED_JOIN_KINDS) - 1 else REQUIRED_JOIN_KINDS[0]

  await RequiredJoin.update_kind(required_join_id, new_kind)
  await required_join_handle_required_join_callback_query(update, context)

@only_admin
async def required_join_handle_edit_join_link_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and update.effective_message and context.user_data is not None

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  await update.effective_message.reply_text("Please enter join link:")

  context.user_data.setdefault("required_join_join_link_edit", int(required_join_id))

  return REQUIRED_JOIN_STATE_EDIT_JOIN_LINK_ENTER

@only_admin
async def required_join_handle_edit_join_link_enter(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message and context.user_data is not None and update.message.text

  target_required_join_id = int(typing.cast(int, context.user_data.get("required_join_join_link_edit")))
  join_link_matches = re.findall(JOIN_LINK_REGEX, update.message.text)

  if not join_link_matches:
    await update.message.reply_text("Invalid link, please try again")
    return

  await RequiredJoin.update_join_link(target_required_join_id, update.message.text)

  (required_join_text, reply_markup) = await _required_join(target_required_join_id)
  await update.effective_message.reply_text(required_join_text, reply_markup=reply_markup)

  context.user_data.pop("required_join_join_link_edit")

  return ConversationHandler.END

@only_admin
async def required_join_handle_edit_target_chat_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and update.effective_message and context.user_data is not None

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  await update.effective_message.reply_text("Please enter target chat (example: @chatname or 12345):") 

  context.user_data.setdefault("required_join_target_chat_edit", int(required_join_id))

  return REQUIRED_JOIN_STATE_EDIT_TARGET_CHAT_ENTER

@only_admin
async def required_join_handle_edit_target_chat_enter(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message and context.user_data is not None and update.message.text

  target_required_join_id = int(typing.cast(int, context.user_data.get("required_join_target_chat_edit")))
  target_chat_matches = re.findall(CHAT_REGEX, update.message.text)

  if update.message.text.lstrip("-").isnumeric():
    await RequiredJoin.update_target_chat(target_required_join_id, update.message.text)
  elif target_chat_matches:
    await RequiredJoin.update_target_chat(target_required_join_id, target_chat_matches[0])
  else:
    await update.message.reply_text("Invalid chat")
    return

  (required_join_text, reply_markup) = await _required_join(target_required_join_id)
  await update.effective_message.reply_text(required_join_text, reply_markup=reply_markup)

  context.user_data.pop("required_join_target_chat_edit")

  return ConversationHandler.END

@only_admin
async def required_join_handle_edit_end_time(update: Update, context: Context):
  assert update.callback_query and update.effective_message and context.matches is not None and context.user_data is not None

  await update.callback_query.answer()

  required_join_id = int(context.matches[0].groups(0)[0])

  await update.effective_message.reply_text("Please enter end time (example: 2024-05-20)") 

  context.user_data.setdefault("required_join_end_time_edit", int(required_join_id))

  return REQUIRED_JOIN_STATE_EDIT_END_TIME_ENTER

@only_admin
async def required_join_handle_edit_end_time_enter(update: Update, context: Context):
  assert update.effective_message and update.effective_message.text and context.user_data is not None

  target_required_join_id = typing.cast(int, context.user_data.pop("required_join_end_time_edit"))

  try:
    end_time = datetime.datetime.fromisoformat(update.effective_message.text)
  except:
    await update.effective_message.reply_text("Invalid date format")
    return

  await RequiredJoin.update_target_end_time(target_required_join_id, end_time)

  (required_join_text, reply_markup) = await _required_join(target_required_join_id)
  await update.effective_message.reply_text(required_join_text, reply_markup=reply_markup)

  return ConversationHandler.END
