from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.account.model import Account
from mediabot.features.language.model import LANGUAGE_STATE_CREATE_CODE, LANGUAGE_STATE_CREATE_NAME, Language
from mediabot.utils import chunks

async def _language_handle_change_language(context: Context):
  languages = await Language.get_all(context.instance.id)

  account = context.account

  inline_buttons = [
    [InlineKeyboardButton(languages[outer*3+inner].name + ("✅" if account.language and account.language.id == languages[outer*3+inner].id else ""), \
      callback_data=f"language_update_{languages[outer*3+inner].id}") for inner in range(min(3, len(languages) - (outer*3)))] \
          for outer in range(max(len(languages), round(len(languages) / 3)))
  ]

  change_language_text = context.l("language.change_text")
  reply_markup = InlineKeyboardMarkup(inline_buttons)

  return (change_language_text, reply_markup, )

async def language_handle_change_language_command(update: Update, context: Context) -> None:
  assert update.effective_message

  (change_language_text, reply_markup,) = await _language_handle_change_language(context)

  await update.effective_message.reply_html(change_language_text, reply_markup=reply_markup)

async def language_handle_change_language_update_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches and update.effective_user

  await update.callback_query.answer()

  language_id = int(context.matches[0].groups(0)[0])

  await Account.set_language_origin(context.account.id, language_id)

  context.account = await Account.get(context.instance.id, update.effective_user.id)

  (change_language_text, reply_markup,) = await _language_handle_change_language(context)

  # if the user selects currently active language button, message content would be the same and
  # telegram would return error because of the same content, so we supress the error
  try:
    await update.callback_query.edit_message_text(change_language_text, reply_markup=reply_markup)
  except:
    pass

@only_admin
async def language_handle_languages_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  languages = await Language.get_all(context.instance.id)

  languages_text = f"🗣 <b>Languages:</b>\n\n"

  inline_buttons = [[InlineKeyboardButton(f"🗑 {language.id}", callback_data=f"language_delete_{language.id}")\
      for language in row] for row in chunks(languages, 5)]

  inline_buttons = [
    [InlineKeyboardButton(f"{language.name} ({language.code}) - 🗑", callback_data=f"language_delete_{language.id}")] for language in languages
  ]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="language_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  await update.callback_query.edit_message_text(languages_text, reply_markup=reply_markup)

@only_admin
async def language_handle_create_callback_query(update: Update, context: Context):
  assert update.effective_message

  await update.effective_message.reply_text("Please enter language name (🇨🇳 Chinese for example):")

  return LANGUAGE_STATE_CREATE_NAME

@only_admin
async def language_handle_create_name_message(update: Update, context: Context):
  assert update.message and context.user_data is not None

  if not update.message.text:
    await update.message.reply_text("Invalid language name, please try again:")
    return LANGUAGE_STATE_CREATE_NAME

  context.user_data.setdefault("language_create_name", update.message.text)

  await update.message.reply_text("Please enter two-letter language code (CN for example):")

  return LANGUAGE_STATE_CREATE_CODE

@only_admin
async def language_handle_create_code_message(update: Update, context: Context):
  assert update.message and context.user_data

  if not update.message.text or len(update.message.text) != 2:
    await update.message.reply_text("Invalid language code, please try again.")
    return LANGUAGE_STATE_CREATE_CODE

  language_name = context.user_data.pop("language_create_name")
  language_code = update.message.text.lower()

  await Language.create(context.instance.id, language_name, language_code)

  await update.effective_message.reply_text("Success")

  return ConversationHandler.END

@only_admin
async def language_handle_delete_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  language_id = int(context.matches[0].groups(0)[0])

  await Language.delete(language_id)

  await language_handle_languages_callback_query(update, context)

@only_admin
async def language_handle_cancel_command(update: Update, context: Context):
  assert update.message

  await update.message.reply_text("Operation cancelled")

  return ConversationHandler.END