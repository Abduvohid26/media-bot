from telegram import Update
from telegram.constants import ChatType

from mediabot.context import Context
from mediabot.features.group.model import Group

async def group_update_handler(update: Update, context: Context) -> None:
  if update.effective_chat and update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
    created_group_id = await Group.try_create(context.instance.id, update.effective_chat.id)

    if created_group_id:
      context.logger.info(None, extra=dict(
        action="GROUP_CREATED",
        group_id=created_group_id,
        group_telegram_id= update.effective_chat.id,
      ))
