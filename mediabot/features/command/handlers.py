import typing
from telegram import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Update
from telegram.ext import ConversationHandler, ApplicationHandlerStop
from telegram.constants import BotCommandLimit

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.command.model import COMMAND_STATE_NAME, Command
from mediabot.features.message.model import Message as MessageModel
from mediabot.features.message.constants import MESSAGE_KIND_COMMAND

async def command_handle_dynamic_command_message(update: Update, context: Context) -> None:
  assert update.message and update.message.from_user and update.message.text

  command = update.message.text.split(" ")[0]

  command_messages = await Command.get_messages_for(context.instance.id, update.message.from_user.id, command)

  for command_message in command_messages:
    deserialized_message = Message.de_json(command_message.message, context.bot)
    assert deserialized_message, "unable to deserialize dynamic command message)"

    if command_message.is_forward:
      deserialized_message = Message.de_json(command_message.message, context.bot)
      assert deserialized_message, "command message is not serializable"
      await context.bot.forward_message(update.message.chat.id, deserialized_message.chat.id, deserialized_message.message_id)
      continue

    await MessageModel.send_from_message(update.message.chat.id, deserialized_message, context.bot)

  raise ApplicationHandlerStop()

async def _command(command_id: int) -> typing.Union[str, InlineKeyboardMarkup]:
  command = await Command.get(command_id)
  assert command, f"command does not exist ({command_id})"

  inline_buttons = [
    [
      InlineKeyboardButton("❌ Disable" if command.is_enabled else "✅ Enable", callback_data=f"command_is_enabled_toggle_{command.id}_{str(int(command.is_enabled))}"),
      InlineKeyboardButton(f"📩 Messages ({command.message_count})", callback_data=f"messages_{MESSAGE_KIND_COMMAND}_{command_id}"),
    ]
  ]

  inline_buttons.extend([[
    InlineKeyboardButton("⬅️ Back", callback_data=f"command"),
    InlineKeyboardButton("🗑 Delete", callback_data=f"command_delete_{command.id}"),
  ]])

  reply_markup = InlineKeyboardMarkup(inline_buttons)
  command_text = f"<b>Command</b>: {'<s>' if not command.is_enabled else ''} {command.command}{'</s>' if not command.is_enabled else ''}\n"
  command_text += f"<b>Created at</b>: {command.created_at}"

  return (command_text, reply_markup,)

@only_admin
async def command_handle_command_create_callback_query(update: Update, context: Context) -> object:
  assert update.effective_message

  await update.callback_query.answer()

  await update.effective_message.reply_text("Please enter the command name:", protect_content=True)

  return COMMAND_STATE_NAME

@only_admin
async def command_handle_command_create_name_message(update: Update, context: Context) -> object:
  assert update.effective_message and update.effective_message.text

  if len(update.message.text) < BotCommandLimit.MIN_COMMAND and len(update.message.text) > BotCommandLimit.MAX_COMMAND:
    await update.effective_message.reply_text(f"Invalid command length (must be >= {BotCommandLimit.MIN_COMMAND} and <= {BotCommandLimit.MAX_COMMAND})")
    return

  command = "/" + str(update.message.text).replace("/", "").replace(" ", "")

  existing_command = await Command.get_by_command(context.instance.id, command)
  if existing_command:
    await update.message.reply_text("Command already exists")
    return COMMAND_STATE_NAME

  created_command_id = await Command.create(context.instance.id, command)

  (command_text, reply_markup) = await _command(created_command_id)
  await update.effective_message.reply_text(command_text, reply_markup=reply_markup)

  return ConversationHandler.END

@only_admin
async def command_handle_commands_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()

  commands = await Command.get_all(context.instance.id, 0, 10)

  commands_text = f"🗃 <b>Commands</b>:\n\n"
  for command in commands:
    commands_text += f"{command.id}) {'<s>' if not command.is_enabled else ''} <b>{command.command}</b> {'</s>' if not command.is_enabled else ''}\n"
    commands_text += f"<b>Messages:</b> {command.message_count}\n"
    commands_text += f"<b>Created at:</b> {command.created_at}\n"
    commands_text += f"\n"

  inline_buttons = [
    [InlineKeyboardButton("✏️ " + str(commands[outer*4+inner].id), callback_data=f"command_{commands[outer*4+inner].id}")
      for inner in range(min(4, len(commands) - (outer*4)))] for outer in range(max(len(commands), round(len(commands) / 4)))
  ]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="command_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  await update.callback_query.edit_message_text(commands_text, reply_markup=reply_markup)

@only_admin
async def command_handle_command_callback_query(update: Update, context: Context, command_id: typing.Union[int, None] = None) -> None:
  assert (update.callback_query and context.matches and context.user_data is not None)

  if isinstance(update.callback_query, CallbackQuery):
    await update.callback_query.answer()

  command_id = command_id or int(context.matches[0].group(1))
  (command_text, reply_markup) = await _command(command_id)
  await update.callback_query.edit_message_text(command_text, reply_markup=reply_markup)

@only_admin
async def command_handle_command_delete_callback_query(update: Update, context: Context) -> None:
  assert(update.callback_query and context.matches)

  await update.callback_query.answer()

  instance = context.instance

  command_id = int(context.matches[0].group(1))
  await Command.delete(instance.id, command_id)

  await command_handle_commands_callback_query(update, context)

@only_admin
async def command_handle_command_is_enabled_toggle(update: Update, context: Context) -> None:
  assert(update.callback_query and context.matches)

  await update.callback_query.answer()

  instance = context.instance

  command_id = int(context.matches[0].group(1))
  is_enabled = bool(int(context.matches[0].group(2)))

  await Command.set_is_enabled(instance.id, command_id, not is_enabled)

  await Command.sync_commands(instance.id, context.bot)

  await command_handle_command_callback_query(update, context, command_id)
