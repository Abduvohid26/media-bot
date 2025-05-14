import logging
import typing
import gettext
import aiolimiter

from telegram.ext import CallbackContext, ExtBot, Application

from mediabot.logger import MergingLoggerAdapter
from mediabot.features.instance.model import INSTANCE_CONTEXT, INSTANCE_LOGGER_CONTEXT, _Instance

class Context(CallbackContext[ExtBot, dict, dict, dict]):
  # cached account
  _account = None

  # cached instance
  _instance: typing.Union[_Instance, None] = None

  _translations = {
    "uz": gettext.translation("base", "locales", languages=["uz"]).gettext,
    "ru": gettext.translation("base", "locales", languages=["ru"]).gettext,
    "en": gettext.translation("base", "locales", languages=["en"]).gettext
  }

  _batch_limiter: typing.Union[aiolimiter.AsyncLimiter, None] = None

  def __init__(self, application: Application, chat_id: typing.Optional[int] = None, user_id: typing.Optional[int] = None, *args):
    super().__init__(application=application, chat_id=chat_id, user_id=user_id)

  @property
  def account(self):
    # TODO: dirty but fixes circular import errors
    from mediabot.features.account.model import _Account
    return typing.cast(_Account, self._account)

  @account.setter
  def account(self, _account):
    self._account = _account

  @property
  def instance(self) -> _Instance:
    return self._instance

  @instance.setter
  def instance(self, _instance):
    self._instance = _instance

  @instance.getter
  def batch_limiter(self):
    if not self._batch_limiter:
      self._batch_limiter = aiolimiter.AsyncLimiter(20, 1)
      return self._batch_limiter

    return self._batch_limiter

  @property
  def bot_instance(self):
    return self.bot_data.get(INSTANCE_CONTEXT)

  def l(self, msgid: str):
    assert self.account

    language_code = self.account.language.code if self.account.language else "en"

    if language_code in self._translations:
      return self._translations[language_code](msgid)

    return self._translations["en"](msgid)

  @property
  def logger(self) -> MergingLoggerAdapter:
    assert self.bot_data

    return self.bot_data.get(INSTANCE_LOGGER_CONTEXT, logging.Logger(""))

  def set_pending_request(self, request, exp: int = 20):
    self.bot_data.setdefault("pending_requests", {})

    async def _cleanup_pending_request(context: CallbackContext, *args, **kwargs):
      self.bot_data.setdefault("pending_requests", {})

      if not self._user_id in self.bot_data["pending_requests"]:
        return

      if not request in self.bot_data["pending_requests"][self._user_id]:
        return

      del self.bot_data["pending_requests"][self._user_id][request]

    self.bot_data["pending_requests"].setdefault(self._user_id, {})

    self.bot_data["pending_requests"][self._user_id][request] = request
    self.job_queue.run_once(_cleanup_pending_request, exp)

  def unset_pending_request(self, request):
    if not "pending_requests" in self.bot_data:
      return

    if not self._user_id in self.bot_data["pending_requests"]:
      return

    if not request in self.bot_data["pending_requests"][self._user_id]:
      return

    del self.bot_data["pending_requests"][self._user_id][request]

  def get_pending_requests(self):
    if not "pending_requests" in self.bot_data:
      return []

    if not self._user_id in self.bot_data["pending_requests"]:
      return []

    return list(self.bot_data["pending_requests"][self._user_id].values())
