import typing
from telegram import Update
from telegram.ext import ApplicationHandlerStop

from mediabot.context import Context
from mediabot.features.instance.model import INSTANCE_ID_CONTEXT, Instance

async def instance_update_handler(update: Update, context: Context) -> None:
  instance_id = typing.cast(int, context.bot_data.get(INSTANCE_ID_CONTEXT))
  instance = await Instance.get(instance_id)
  assert instance

  context.instance = instance

  if update.effective_message and update.effective_message.caption == "#media-service":
    raise ApplicationHandlerStop()
