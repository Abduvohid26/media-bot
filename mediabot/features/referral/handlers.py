import typing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
from telegram.ext import ConversationHandler

from mediabot.context import Context
from mediabot.decorators import only_admin
from mediabot.features.referral.model import CREATE_REFERRAL_STATE_ENTER, Referral
from mediabot.utils import chunks
from mediabot.features.account.model import Account

async def referral_handle_update(update: Update, context: Context) -> None:
  if not update.message or not update.message.text:
    return

  if not update.message.text.startswith("/start"):
    return

  start_command_chunks = update.message.text.split(" ")

  if len(start_command_chunks) != 2 or len(start_command_chunks[1]) < 1:
    return

  referral = await Referral.get_by_code(context.instance.id, start_command_chunks[1])

  if not referral:
    return

  await Account.set_referral_origin(context.instance.id, context.account.id, referral.id)
  await Referral.create_click(context.instance.id, referral.id, context.account.id)

@only_admin
async def referral_handle_referrals_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()

  referrals = await Referral.get_all(context.instance.id, 0, 15)

  referrals_text = f"🧵 <b>Referrals:</b>\n\n"
  for referral in referrals:
    referrals_text += f"{referral.id}) <b>{referral.code}</b>\n"
    referrals_text += f"<b>Clicks</b>: {referral.click_count}\n"
    referrals_text += f"<b>Created at</b>: {referral.created_at}\n"
    referrals_text += f"\n"

  inline_buttons = [[InlineKeyboardButton(f"✏️ {referral.id}", callback_data=f"referral_{referral.id}")\
      for referral in row] for row in chunks(referrals, 5)]

  inline_buttons.append([
    InlineKeyboardButton("⬅️ Back", callback_data="control_panel"),
    InlineKeyboardButton("🆕 Create", callback_data="referral_create")
  ])

  reply_markup = InlineKeyboardMarkup(inline_buttons)

  await update.callback_query.edit_message_text(referrals_text, reply_markup=reply_markup)

@only_admin
async def referral_handle_create_callback_query(update: Update, context: Context):
  assert update.effective_message

  await update.effective_message.reply_text("Please enter referral code (/cancel to cancel the operation):")

  return CREATE_REFERRAL_STATE_ENTER

@only_admin
async def referral_handle_create_enter_message(update: Update, context: Context) -> typing.Union[int, None]:
  assert update.message

  referral_code = str(update.message.text).replace(" ", "")
  existing_referral = await Referral.get_by_code(context.instance.id, referral_code)

  if existing_referral:
    await update.message.reply_text("Referral already exists with this code")
    return

  await Referral.create(context.instance.id, referral_code)
  await update.message.reply_text("Done")

  return ConversationHandler.END

@only_admin
async def referral_handle_create_cancel(update: Update, context: Context):
  assert update.message

  await update.message.reply_text("Cancelled")

  return ConversationHandler.END

@only_admin
async def referral_handle_delete(update: Update, context: Context):
  assert update.callback_query and context.matches

  await update.callback_query.answer()

  referral_id = int(context.matches[0].groups(0)[0])

  if isinstance(update.callback_query.message, Message):
    await Referral.delete(referral_id)
    await referral_handle_referrals_callback_query(update, context)

@only_admin
async def referral_handle_referral_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and context.matches

  await update.callback_query.answer()
  
  referral_id = int(context.matches[0].groups(0)[0])
  target_referral = await Referral.get_detailed(referral_id)
  assert target_referral

  referral_text = f"{target_referral.id}) <b>{target_referral.code}</b>\n"
  referral_text += f"<b>Link:</b> <code>https://t.me/{context.instance.username}?start={target_referral.code}</code>\n"

  if target_referral.account_new_statistics:
    referral_text += "<b>New accounts:</b>\n"
    for account_new_statistics in target_referral.account_new_statistics:
      referral_text += f"- {account_new_statistics.language_name}: {account_new_statistics.account_count}\n"

    referral_text += "\n"

  if target_referral.account_click_statistics:
    referral_text += "<b>Clicks:</b>\n"
    for account_click_statistics in target_referral.account_click_statistics:
      referral_text += f"- {account_click_statistics.language_name}: {account_click_statistics.account_count}\n"

  referral_text += f"<b>Created at</b>: {target_referral.created_at}\n"

  control_buttons = [
    [
      InlineKeyboardButton("🗑 Delete", callback_data=f"referral_delete_{target_referral.id}")
    ],
    [
      InlineKeyboardButton("⬅️ Back", callback_data=f"referral"),
    ]
  ]

  control_markup = InlineKeyboardMarkup(control_buttons)
  await update.callback_query.edit_message_text(referral_text, reply_markup=control_markup)
