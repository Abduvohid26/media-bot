import aiolimiter

from telegram.ext import BaseRateLimiter

COVERED_ENDPOINTS = [
  "sendPhoto",
  "sendMessage",
  "sendAudio",
  "sendVideo",
  "sendChatAction",
  "sendContract",
  "sendAnimation",
  "sendDice",
  "sendInvoice",
  "sendLocation",
  "sendMediaGroup",
  "sendPoll",
  "sendSticker",
  "sendDocument",
  "editMessageText",
  "editMessageCaption",
  "deleteMessage",
  "approveChatJoinRequest",
  "declineChatJoinRequest"
]

class RateLimiter(BaseRateLimiter):
  rate_limiter = aiolimiter.AsyncLimiter(28, 1)

  async def initialize(self):
    pass

  async def shutdown(self):
    pass

  async def process_request(self, callback, args, kwargs, endpoint, data, rate_limit_args):
    if endpoint in COVERED_ENDPOINTS:
      async with self.rate_limiter:
        return await callback(*args, **kwargs)

    return await callback(*args, **kwargs)