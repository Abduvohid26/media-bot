import typing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ConversationHandler

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.language.model import Language

from mediabot.features.message.constants import MESSAGE_KIND_ADVERTISEMENT, MESSAGE_KIND_COMMAND, \
    MESSAGE_KIND_JOIN_REQUEST, MESSAGE_KIND_REQUIRED_JOIN, MESSAGE_CONTEXT_KIND, MESSAGE_CONTEXT_ORIGIN

from mediabot.features.message.model import CP_MESSAGE_LANGUAGE_EDIT_CONTEXT, \
  CP_MESSAGE_MESSAGE_EDIT_CONTEXT, MESSAGE_STATE_LANGUAGE_EDIT, \
  MESSAGE_STATE_MESSAGE_ADD, MESSAGE_STATE_MESSAGE_EDIT, Message as MessageModel

MESSAGE_CONTEXT_EDIT_MESSAGE_ID = object()
MESSAGE_CONTEXT_EDIT_MESSAGE_KIND = object()
MESSAGE_CONTEXT_EDIT_MESSAGE_ORIGIN = object()
MESSAGE_CONTEXT_EDIT_LANGUAGE_ID = object()

async def _message(message_kind: int, origin: int, message_id: int):
  message = await MessageModel.get(message_id)
  assert message, f"message not found ({message_id})"

  message_text = f"{message.id}) <b>{MessageModel.get_preview_from(message.message)}</b>\n"
  message_text += f"<b>Type</b>: {MessageModel.get_type_from(message.message)}\n"
  message_text += f"<b>Language</b>: {message.language.name + ' ' + f'({message.language.code})' if message.language else '-'}\n"
  message_text += f"<b>Created at</b>: {message.created_at}\n\n"

  inline_buttons = [
    [
      InlineKeyboardButton("✉️ Edit message", callback_data=f"message_message_edit_{message_kind}_{origin}_{message_id}"),
      InlineKeyboardButton("🌏 Edit language", callback_data=f"message_language_edit_{message_id}"),
    ],
    # for is_attach, is_forward and is_after_join buttons
    [],
    [
      InlineKeyboardButton("⬅️ Back", callback_data=f"messages_{message_kind}_{origin}"),
      InlineKeyboardButton("🗑 Delete", callback_data=f"message_delete_{message_kind}_{origin}_{message_id}")
    ]
  ]

  if message_kind in [MESSAGE_KIND_ADVERTISEMENT]:
    inline_buttons[1].append(InlineKeyboardButton(f"📎 Attach: {'Yes' if message.is_attach else 'No'}", callback_data=f"message_is_attach_toggle_{message_kind}_{origin}_{message_id}_{int(message.is_attach)}"))

  if message_kind in [MESSAGE_KIND_ADVERTISEMENT, MESSAGE_KIND_COMMAND, MESSAGE_KIND_JOIN_REQUEST, MESSAGE_KIND_REQUIRED_JOIN]:
    inline_buttons[1].append(InlineKeyboardButton(f"⏩ Forward: {'Yes' if message.is_forward else 'No'}", callback_data=f"message_is_forward_toggle_{message_kind}_{origin}_{message_id}_{int(message.is_forward)}"))

  if message_kind in [MESSAGE_KIND_REQUIRED_JOIN]:
    inline_buttons[1].append(InlineKeyboardButton(f"↩️ After join: {'Yes' if message.is_after_join else 'No'}", callback_data=f"message_is_after_join_toggle_{message_kind}_{origin}_{message_id}_{int(message.is_after_join)}"))

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (message_text, reply_markup)

async def _messages(context: Context, message_kind: int, origin: int):
  messages = await MessageModel.get_messages(message_kind, origin, 0, 10)
  messages_text = f"✉️ <b>Messages</b>:\n\n"

  for message in messages:
    messages_text += f"{message.id}) <b>{MessageModel.get_preview_from(message.message)}</b>\n"
    messages_text += f"<b>Type</b>: {MessageModel.get_type_from(message.message)}\n"
    messages_text += f"<b>Language</b>: {message.language.name + ' ' + f'({message.language.code})' if message.language else '-'}\n"
    messages_text += f"<b>Created at</b>: {message.created_at}\n\n"

  inline_buttons = [
    [InlineKeyboardButton("✏️ " + str(messages[outer*4+inner].id), callback_data=f"message_{message_kind}_{origin}_{messages[outer*4+inner].id}")
      for inner in range(min(4, len(messages) - (outer*4)))] for outer in range(max(len(messages), round(len(messages) / 4)))
  ]

  back_button_callback_data = ""
  if message_kind == MESSAGE_KIND_COMMAND:
    back_button_callback_data = f"command_{origin}"
  elif message_kind == MESSAGE_KIND_REQUIRED_JOIN:
    back_button_callback_data = f"required_join_{origin}"
  elif message_kind == MESSAGE_KIND_JOIN_REQUEST:
    back_button_callback_data = f"join_request_{origin}"
  elif message_kind == MESSAGE_KIND_ADVERTISEMENT:
    back_button_callback_data = f"advertisement_{origin}"

  inline_buttons.append([
    InlineKeyboardButton(f"⬅️ Back", callback_data=back_button_callback_data),
    InlineKeyboardButton(f"➕ Add message", callback_data=f"message_add_{message_kind}_{origin}")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (messages_text, reply_markup)

@only_admin
async def message_handle_messages_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))

  (messages_text, reply_markup) = await _messages(context, message_kind, origin)

  await update.callback_query.edit_message_text(messages_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_callback_query(update: Update, context: Context, message_id: typing.Union[int, None] = None) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))
  message_id = int(context.matches[0].group(3))

  (message_text, reply_markup) = await _message(message_kind, origin, message_id)

  await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_is_attach_toggle_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))
  message_id = int(context.matches[0].group(3))
  is_attach = bool(int(context.matches[0].group(4)))

  await MessageModel.update_is_attach(message_id, not is_attach)

  await update.callback_query.answer("✅ Success")

  (message_text, reply_markup) = await _message(context, message_kind, origin, message_id)

  await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_is_forward_toggle_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))
  message_id = int(context.matches[0].group(3))
  is_forward = bool(int(context.matches[0].group(4)))

  await MessageModel.update_is_forward(message_id, not is_forward)

  await update.callback_query.answer("✅ Success")

  (message_text, reply_markup) = await _message(context, message_kind, origin, message_id)

  await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_is_after_join_toggle_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))
  message_id = int(context.matches[0].group(3))
  is_after_join = bool(int(context.matches[0].group(4)))

  await MessageModel.update_is_after_join(message_id, not is_after_join)

  await update.callback_query.answer("✅ Success")

  (message_text, reply_markup) = await _message(context, message_kind, origin, message_id)
  await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_edit_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  message_kind = int(context.matches[0].groups(0)[0])
  message_origin = int(context.matches[0].groups(1)[1])
  message_id = int(context.matches[0].groups(2)[2])

  context.user_data.setdefault(MESSAGE_CONTEXT_EDIT_MESSAGE_KIND, message_kind)
  context.user_data.setdefault(MESSAGE_CONTEXT_EDIT_MESSAGE_ORIGIN, message_origin)
  context.user_data.setdefault(MESSAGE_CONTEXT_EDIT_MESSAGE_ID, message_id)

  await update.effective_message.reply_text("Please send/forward the message:")

  return MESSAGE_STATE_MESSAGE_EDIT

@only_admin
async def message_handle_message_edit_enter_message(update: Update, context: Context) -> int:
  assert update.message

  message_id = context.user_data.get(MESSAGE_CONTEXT_EDIT_MESSAGE_ID, 0)

  await MessageModel.update_message(message_id, update.message.to_json())

  message_kind = context.user_data.pop(MESSAGE_CONTEXT_EDIT_MESSAGE_KIND)
  message_origin = context.user_data.pop(MESSAGE_CONTEXT_EDIT_MESSAGE_ORIGIN)
  message_id = context.user_data.pop(MESSAGE_CONTEXT_EDIT_MESSAGE_ID)

  (message, reply_markup,) = await _message(message_kind, message_origin, message_id)
  await update.message.reply_text(message, reply_markup=reply_markup)

  return ConversationHandler.END

@only_admin
async def message_handle_language_edit_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  message_id = int(context.matches[0].groups(0)[0])
  languages = await Language.get_all(context.instance.id)

  keyboard_buttons = [
    [KeyboardButton(languages[outer*3+inner].name) for inner in range(min(3, len(languages) - (outer*3)))] \
        for outer in range(max(len(languages), round(len(languages) / 3)))
  ]

  keyboard_buttons.append([KeyboardButton("🏳️")])

  reply_markup = ReplyKeyboardMarkup(keyboard_buttons)

  await update.effective_message.reply_text("Please select message language:", reply_markup=reply_markup)

  context.user_data.setdefault(MESSAGE_CONTEXT_EDIT_LANGUAGE_ID, message_id)

  return MESSAGE_STATE_LANGUAGE_EDIT

@only_admin
async def message_handle_language_edit_enter_message(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message

  message_id = typing.cast(int, context.user_data.get(MESSAGE_CONTEXT_EDIT_LANGUAGE_ID))

  if update.effective_message.text == "🏳️":
    await MessageModel.update_language_origin(message_id, None)
  else:
    languages = await Language.get_all(context.instance.id)

    target_languages = [language for language in languages if update.message.text == language.name]

    if not target_languages:
      await update.message.reply_text("Invalid language")
      return

    await MessageModel.update_language_origin(message_id, target_languages[0].id)

  context.user_data.pop(MESSAGE_CONTEXT_EDIT_LANGUAGE_ID, None)

  reply_markup = ReplyKeyboardRemove()
  await update.message.reply_text("Done", reply_markup=reply_markup)
  return ConversationHandler.END

@only_admin
async def message_handle_message_delete_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and update.effective_message and context.matches

  await update.callback_query.answer()

  message_kind = int(context.matches[0].group(1))
  origin = int(context.matches[0].group(2))
  message_id = int(context.matches[0].group(3))

  await MessageModel.delete(message_id)

  (messages_text, reply_markup) = await _messages(message_kind, origin)

  await update.effective_message.edit_text(messages_text, reply_markup=reply_markup)

@only_admin
async def message_handle_message_add_callback_query(update: Update, context: Context):
  assert update.callback_query and context.matches and context.user_data is not None

  await update.callback_query.answer()

  message_kind = int(context.matches[0].group(1))
  message_origin = int(context.matches[0].group(2))

  await update.callback_query.message.reply_text("Please send/forward the message:")

  context.user_data[MESSAGE_CONTEXT_KIND] = message_kind
  context.user_data[MESSAGE_CONTEXT_ORIGIN] = message_origin

  return MESSAGE_STATE_MESSAGE_ADD

@only_admin
async def message_handle_message_add_enter_message(update: Update, context: Context) -> int:
  assert update.message

  message_kind = typing.cast(int, context.user_data.get(MESSAGE_CONTEXT_KIND))
  message_origin = typing.cast(int, context.user_data.get(MESSAGE_CONTEXT_ORIGIN))

  await MessageModel.create(context.instance.id, message_kind, message_origin, update.message.to_json())

  await update.message.reply_text("Done")

  context.user_data.pop(MESSAGE_CONTEXT_KIND, None)
  context.user_data.pop(MESSAGE_CONTEXT_ORIGIN, None)

  return ConversationHandler.END
