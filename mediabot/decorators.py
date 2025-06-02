from functools import wraps
from telegram import Update
from mediabot.context import Context
from mediabot.exceptions import AccessDeniedException
from mediabot.features.account.model import ACCOUNT_SYS_ID_LIST
from mediabot.cache import redis

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



def job_check(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            user_id = args[3]
        except IndexError:
            raise Exception("user_id topilmadi. Decorator noto'g'ri ishlatilgan.")

        current_job = await redis.get(f"user:{user_id}:job")
        if current_job:
            context = args[0]
            chat_id = args[2]
            await context.bot.send_message(chat_id, "Yuqoridagi sorov tugashini kuting ????")
            return  
        return await func(*args, **kwargs)  
    return wrapper


def job_check_youtbe(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            user_id = args[2]
        except IndexError:
            raise Exception("user_id topilmadi. Decorator noto'g'ri ishlatilgan.")

        current_job = await redis.get(f"user:{user_id}:job")
        if current_job:
            context = args[0]
            chat_id = args[1]
            await context.bot.send_message(chat_id, "Yuqoridagi sorov tugashini kuting ????")
            return  
        return await func(*args, **kwargs)  
    return wrapper