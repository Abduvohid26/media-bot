from functools import wraps
from telegram import Update
from mediabot.context import Context
from mediabot.exceptions import AccessDeniedException
from mediabot.features.account.model import ACCOUNT_SYS_ID_LIST

def only_admin(func):
  @wraps(func)
  async def wrapped(update: Update, context: Context, *args, **kwargs):
    assert update.effective_user

    if not context.account.is_admin and not update.effective_user.id in ACCOUNT_SYS_ID_LIST:
      raise AccessDeniedException()

    return await func(update, context, *args, **kwargs)
  return wrapped

def only_sys(func):
  @wraps(func)
  async def wrapped(update: Update, context: Context, *args, **kwargs):
    assert update.effective_user

    if not update.effective_user.id in ACCOUNT_SYS_ID_LIST:
      raise AccessDeniedException()

    return await func(update, context, *args, **kwargs)
  return wrapped

def check_pending_request(request):
  def decorator(func):
    async def wrapper(update: Update, context: Context, *args, **kwargs):
      pending_requests = context.get_pending_requests()

      for pending_request in pending_requests:
        if isinstance(pending_request, request):
          await update.effective_message.reply_text("<b>❗️ Please wait the previous request to finish.</b>")
          return

      return await func(update, context, *args, **kwargs)
    return wrapper
  return decorator
