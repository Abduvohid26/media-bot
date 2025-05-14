import traceback

from telegram.ext import ApplicationHandlerStop

from mediabot.context import Context
from mediabot.exceptions import AccessDeniedException, InstanceRequestRateLimitReached, InstanceQuotaLimitReachedException

async def error_handle_error(update: object, context: Context) -> None:
  if isinstance(context.error, InstanceQuotaLimitReachedException):
    context.logger.warn(None, extra=dict(
      action="INSTANCE_QUOTA_REACHED"
    ))
  elif isinstance(context.error, InstanceRequestRateLimitReached):
    context.logger.error(None, extra=dict(
      action="INSTANCE_REQUEST_RATE_LIMIT_REACHED"
    ))

  elif isinstance(context.error, AccessDeniedException):
    pass

  else:
    context.logger.error(None, extra=dict(
      action="UNKNOWN_ERROR",
      # chat_id=update.effective_chat.id,
      # uesr_id=update.effective_user.id,
      stack_trace=traceback.format_exc()
    ))

  raise ApplicationHandlerStop()
