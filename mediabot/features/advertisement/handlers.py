import typing
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ConversationHandler

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.advertisement.model import Advertisement, ADVERTISEMENT_STATE_CREATE_NAME
from mediabot.features.message.model import Message as MessageModel
from mediabot.features.message.constants import MESSAGE_KIND_ADVERTISEMENT

CANCEL_CHARACTER = "❌"
ADVERTISEMENT_MAX_COUNT = 10

async def advertisement_message_copy(context: Context, kind: int, chat_id: int, from_chat_id: int, message_id: int):
  advertisement_messages = await Advertisement.get_all_messages_for(context.instance.id, kind, context.account.id)
  attach_messages = [message for message in advertisement_messages \
      if message.is_attach and (not message.is_seen if message.is_onetime else True)]
  after_messages = [message for message in advertisement_messages if not message.is_attach \
      and (not message.is_seen if message.is_onetime else True)]
  attach_message = random.choice(attach_messages) if attach_messages else None

  attach_message_caption = ""
  attach_message_reply_markup = None
  attach_message_caption_entities = None

  if attach_message:
    deserialized_attach_message = Message.de_json(attach_message.message, context.bot)
    assert deserialized_attach_message, "unable to deserialized advertisement attach message"

    attach_message_caption = deserialized_attach_message.caption or deserialized_attach_message.text
    attach_message_reply_markup = deserialized_attach_message.reply_markup
    # TODO(mhw0): this doesn't work on attach
    attach_message_caption_entities = deserialized_attach_message.caption_entities or deserialized_attach_message.entities

  # TODO(mhw0): handle the copy error and report it
  await context.bot.copy_message(chat_id, from_chat_id, message_id, caption=attach_message_caption, \
      reply_markup=attach_message_reply_markup, caption_entities=attach_message_caption_entities)

  if attach_message:
    await MessageModel.try_create_message_seen(attach_message.id, context.account.id, context.instance.id)

  for after_message in after_messages:
    deserialized_after_message = Message.de_json(after_message.message, context.bot)
    assert deserialized_after_message, "unable to deserialize advertisement after message"

    if after_message.is_forward:
      # TODO(mhw0): handle the copy error and report it
      message = await context.bot.forward_message(chat_id, deserialized_after_message.chat_id, deserialized_after_message.message_id)
    else:
      message = await MessageModel.send_from_message(chat_id, deserialized_after_message, context.bot)

    await MessageModel.try_create_message_seen(after_message.id, context.account.id, context.instance.id)
    return message

async def advertisement_message_send(context: Context, chat_id: int, kind: int, *args, **kwargs) -> Message:
  advertisement_messages = await Advertisement.get_all_messages_for(context.instance.id, kind, context.account.id)

  attach_messages = [message for message in advertisement_messages \
      if message.is_attach and (not message.is_seen if message.is_onetime else True)]
  attach_message = random.choice(attach_messages) if attach_messages else None

  if attach_message:
    deserialized_attach_message = typing.cast(Message, Message.de_json(attach_message.message, context.bot))

    if "text" in kwargs:
      kwargs["text"] = kwargs["text"] + "\n" + (deserialized_attach_message.text or deserialized_attach_message.caption or "")
    else:
      kwargs["caption"] = kwargs.get("caption", "") + "\n" + (deserialized_attach_message.text or deserialized_attach_message.caption)

    kwargs["reply_markup"] = InlineKeyboardMarkup(kwargs["reply_markup"].inline_keyboard + \
        (deserialized_attach_message.reply_markup.inline_keyboard if deserialized_attach_message.reply_markup else ())) \
            if "reply_markup" in kwargs else deserialized_attach_message.reply_markup

    await MessageModel.try_create_message_seen(attach_message.id, context.account.id, context.instance.id)

  after_messages = [message for message in advertisement_messages if not message.is_attach and (not message.is_seen if message.is_onetime else True)]

  sent_message = None
  if kind == Advertisement.KIND_AUDIO:
    sent_message = await context.bot.send_audio(chat_id=chat_id, *args, **kwargs)
  elif kind == Advertisement.KIND_PHOTO:
    sent_message = await context.bot.send_photo(chat_id=chat_id, *args, **kwargs)
  elif kind == Advertisement.KIND_VIDEO:
    sent_message = await context.bot.send_video(chat_id=chat_id, *args, **kwargs)
  elif kind == Advertisement.KIND_VOICE:
    sent_message = await context.bot.send_voice(chat_id=chat_id, *args, **kwargs)
  elif kind == Advertisement.KIND_TRACK_SEARCH:
    sent_message = await context.bot.send_message(chat_id=chat_id, *args, **kwargs)

  for after_message in after_messages:
    deserialized_message = Message.de_json(after_message.message, context.bot)
    assert deserialized_message, "unable to deserialize advertisement after message"

    if after_message.is_forward:
      await context.bot.forward_message(chat_id, deserialized_message.chat_id, deserialized_message.message_id)
    else:
      await MessageModel.send_from_message(chat_id, deserialized_message, context.bot)

    await MessageModel.try_create_message_seen(after_message.id, context.account.id, context.instance.id)

  return sent_message

async def _advertisement(advertisement_id: int) -> typing.Union[str, InlineKeyboardMarkup]:
  advertisement = await Advertisement.get(advertisement_id)
  assert advertisement, f"unable to find advertisement ({advertisement_id})"

  advertisement_text = f"{'<s>' if not advertisement.is_enabled else ''} {advertisement.id}) {advertisement.name} {'</s>' if not advertisement.is_enabled else ''}\n"
  advertisement_text += f"ℹ️ <b>Kind</b>: {Advertisement.stringify_kind(advertisement.kind)}\n"
  advertisement_text += f"👀 <b>Views</b>: {advertisement.message_seen_count}\n"
  advertisement_text += f"📅 <b>Created at</b>: {advertisement.created_at}\n"

  advertisement_kind_index = Advertisement.KINDS.index(advertisement.kind)

  inline_buttons = [
    [
      InlineKeyboardButton(f"🔌 Enabled: {'Yes' if advertisement.is_enabled else 'No'}", callback_data=f"advertisement_is_enabled_toggle_{advertisement.id}_{int(advertisement.is_enabled)}"),
      InlineKeyboardButton(f"🔠 Kind: {Advertisement.stringify_kind(advertisement.kind)}", callback_data=f"advertisement_kind_toggle_{advertisement.id}_{advertisement_kind_index}"),
    ],
    [
      InlineKeyboardButton(f"✉️ Messages ({advertisement.message_count})", callback_data=f"messages_{MESSAGE_KIND_ADVERTISEMENT}_{advertisement_id}"),
      InlineKeyboardButton(f"🗑 Delete", callback_data=f"advertisement_delete_{advertisement.id}"),
    ],
    [
      InlineKeyboardButton(f"◀ Back", callback_data=f"advertisement"),
      InlineKeyboardButton(f"👀 Clear views", callback_data=f"advertisement_message_seen_clear_{advertisement.id}"),
    ]
  ]

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (advertisement_text, reply_markup)

async def _advertisements(instance_origin: int) -> typing.Union[str, InlineKeyboardMarkup]:
  advertisements = await Advertisement.get_all(instance_origin, 0, 10)

  advertisements_text = f"📑️ <b>Advertisements</b>:\n\n"

  for advertisement_index, advertisement in enumerate(advertisements):
    advertisements_text += f"{'<s>' if not advertisement.is_enabled else ''} {advertisement_index+1}) {advertisement.name} {'</s>' if not advertisement.is_enabled else ''}\n"
    advertisements_text += f"ℹ️ <b>Kind</b>: {Advertisement.stringify_kind(advertisement.kind)}\n"
    advertisements_text += f"✉️ <b>Messages</b>: {advertisement.message_count}\n"
    advertisements_text += f"👀 <b>Views</b>: {advertisement.message_seen_count}\n"
    advertisements_text += f"📅 <b>Created at</b>: {advertisement.created_at}\n\n"

  inline_buttons = [
    [InlineKeyboardButton("✏️ " + str(outer*4+inner+1), callback_data=f"advertisement_{advertisements[outer*4+inner].id}")
      for inner in range(min(4, len(advertisements) - (outer*4)))] for outer in range(max(len(advertisements), round(len(advertisements) / 4)))
  ]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="advertisement_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (advertisements_text, reply_markup)

@only_admin
async def advertisement_handle_create_callback_query(update: Update, context: Context):
  assert update.effective_message

  advertisement_count = await Advertisement.count(context.instance.id)

  if advertisement_count >= ADVERTISEMENT_MAX_COUNT:
    await update.callback_query.answer("⚠️ You reached max number of advertisements, please delete the old ones.", show_alert=True)
    return ConversationHandler.END

  await update.callback_query.answer()

  reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CANCEL_CHARACTER)]], one_time_keyboard=True)

  await update.effective_message.reply_text("Please enter advertisement name:", reply_markup=reply_markup)

  return ADVERTISEMENT_STATE_CREATE_NAME

@only_admin
async def advertisement_handle_create_name(update: Update, context: Context):
  assert update.message and update.message.text

  if update.message.text == CANCEL_CHARACTER:
    await update.effective_message.reply_text("❌ Cancelled", reply_markup=ReplyKeyboardRemove())

    (advertisement_text, reply_markup) = await _advertisements(context.instance.id)
    await update.effective_message.reply_text(advertisement_text, reply_markup=reply_markup)

    return ConversationHandler.END

  created_advertisement_id = await Advertisement.create(context.instance.id, update.message.text)

  await update.message.reply_text("✅ Success", reply_markup=ReplyKeyboardRemove())

  context.logger.debug(None, extra=dict(
    action="ADVERTISEMENT_CREATE",
    advertisement_id=created_advertisement_id,
    advertisement_name=update.message.text,
    user_id=update.effective_user.id
  ))

  (advertisement_text, reply_markup) = await _advertisement(created_advertisement_id)
  await update.effective_message.reply_text(advertisement_text, reply_markup=reply_markup)

  return ConversationHandler.END

@only_admin
async def advertisement_handle_advertisements_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  (advertisements_text, reply_markup) = await _advertisements(context.instance.id)
  await update.callback_query.edit_message_text(advertisements_text, reply_markup=reply_markup)

@only_admin
async def advertisement_handle_advertisement(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and update.callback_query.message and context.user_data is not None

  advertisement_id = int(context.matches[0].groups(0)[0])

  await update.callback_query.answer(f"📑️ Advertisement: #{advertisement_id}")

  (advertisement_text, reply_markup) = await _advertisement(advertisement_id)
  await update.callback_query.edit_message_text(advertisement_text, reply_markup=reply_markup)

@only_admin
async def advertisement_handle_advertisement_message_seen_clear(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer("✅ Success")

  advertisement_id = int(context.matches[0].groups(0)[0])

  await Advertisement.clear_message_seen(advertisement_id)

  (advertisement_text, reply_markup) = await _advertisement(advertisement_id)
  await update.callback_query.edit_message_text(advertisement_text, reply_markup=reply_markup)

@only_admin
async def advertisement_handle_advertisement_delete(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and update.callback_query.message

  await update.callback_query.answer(f"✅ Success")

  advertisement_id = int(context.matches[0].groups(0)[0])
  await Advertisement.delete(advertisement_id)

  (advertisement_text, reply_markup) = await _advertisements(context.instance.id)
  await update.callback_query.edit_message_text(advertisement_text, reply_markup=reply_markup)

@only_admin
async def advertisement_handle_advertisement_is_enabled_toggle(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and update.callback_query.message

  await update.callback_query.answer()

  advertisement_id = int(context.matches[0].groups(0)[0])
  is_enabled = bool(int(context.matches[0].groups(1)[1]))

  await Advertisement.update_is_enabled(advertisement_id, not is_enabled)

  (advertisement_text, reply_markup) = await _advertisement(advertisement_id)
  await update.effective_message.edit_text(advertisement_text, reply_markup=reply_markup)

@only_admin
async def advertisement_handle_advertisement_kind_toggle(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and update.callback_query.message

  await update.callback_query.answer()

  advertisement_id = int(context.matches[0].groups(0)[0])
  advertisement_kind_index = int(context.matches[0].groups(1)[1])

  new_kind = Advertisement.KINDS[0] if len(Advertisement.KINDS) - 1 == advertisement_kind_index \
      else Advertisement.KINDS[advertisement_kind_index+1]

  await Advertisement.update_kind(advertisement_id, None if new_kind == Advertisement.KIND_NONE else new_kind)

  (advertisement_text, reply_markup) = await _advertisement(advertisement_id)
  await update.effective_message.edit_text(advertisement_text, reply_markup=reply_markup)
