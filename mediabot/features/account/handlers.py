import typing
from telegram import Update

from telegram.constants import ChatType, ChatMemberStatus
from telegram.ext import ApplicationHandlerStop

from mediabot.features.account.model import _Account, Account
from mediabot.context import Context

# tries to create an account or gets the existing one
async def account_try_create(context: Context, chat_id: typing.Union[int, str], user_id: int, language_code: typing.Union[str, None] = None) -> _Account:
  created_account_id = await Account.try_create(context.instance.id, user_id, language_code)

  if created_account_id:
    context.logger.info(None, extra={
      "action": "ACCOUNT_CREATED",
      "account_id": created_account_id,
      "chat_id": chat_id,
      "user_id": user_id
    })

  account = await Account.get(context.instance.id, user_id)
  assert account

  return account

async def account_update_handler(update: Update, context: Context) -> None:
  if not (update.effective_chat and update.effective_user):
    raise ApplicationHandlerStop()

  context.account = await account_try_create(context, update.effective_chat.id, update.effective_user.id, update.effective_user.language_code) \
      if update.effective_chat.type in [ChatType.PRIVATE] \
      else await Account.get(context.instance.id, update.effective_user.id)

async def account_my_chat_member_handler(update: Update, context: Context):
  assert update.my_chat_member

  if not context.account:
    return

  if update.my_chat_member.new_chat_member.status in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT, ChatMemberStatus.RESTRICTED]:
    await Account.set_deleted_at(context.account.id)

    context.logger.info(None, extra={
      "action": "ACCOUNT_LEFT",
      "account_id": context.account.id,
      "chat_id": update.my_chat_member.chat.id,
      "user_id": update.my_chat_member.from_user.id
    })

    return

  if update.my_chat_member.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
    await Account.unset_deleted_at(context.account.id)

    context.logger.info(None, extra={
      "action": "ACCOUNT_RECOVER",
      "account_id": context.account.id,
      "chat_id": update.my_chat_member.chat.id,
      "user_id": update.my_chat_member.from_user.id
    })
