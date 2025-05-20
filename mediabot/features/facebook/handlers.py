import traceback
from telegram import Update

import mediabot.features.required_join.handlers as required_join_feature_handlers
import mediabot.features.track.handlers as track_feature
from mediabot.exceptions import InstanceQuotaLimitReachedException
from mediabot.context import Context
from mediabot.features.instance.model import Instance
from mediabot.features.required_join.model import RequiredJoinKind
from mediabot.features.facebook.model import Facebook
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.features.advertisement.model import Advertisement
from mediabot.features.track.model import Track

async def _facebook_download_telegram(context: Context, link: str, chat_id: int, user_id: int, reply_to_message_id=None):
  processing_message = await context.bot.send_message(chat_id, \
      context.l("request.processing_text"), reply_to_message_id=reply_to_message_id)

  try:
    file_id_cache = await Facebook.get_facebook_cache_file_id(context.instance.id, link)

    if file_id_cache:
      sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=file_id_cache)
      await Facebook.set_facebook_cache_file_id(context.instance.id, link, sent_message.video.file_id)
    else:
      file_id = await Facebook.download_telegram(link, context.instance.token)
      sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=file_id)
      await Facebook.set_facebook_cache_file_id(context.instance.id, link, sent_message.video.file_id)

    context.logger.info(None, extra=dict(
      action="FACEBOOK_DOWNLOAD",
      chat_id=chat_id,
      user_id=user_id,
      link=link
    ))
  except Exception:
    context.logger.error(None, extra=dict(
      action="FACEBOOK_DOWNLOAD_FAILED",
      chat_id=chat_id,
      user_id=user_id,
      link=link,
      stack_trace=traceback.format_exc()
    ))

    await context.bot.send_message(chat_id, context.l("request.failed_text"), reply_to_message_id=reply_to_message_id)
    print(traceback.format_exc())
  finally:
    await processing_message.delete()

    #   !!!!!!!!!!!!11 (facek book uchun increaement function yozib qoysish kerak)  await Instance.increment_tiktok_used(context.instance.id) 

  if context.instance.tiktok_recognize_track_feature_enabled:
    try:
      recognize_result = await Track.recognize_by_link(link)
      await track_feature.track_recognize_from_recognize_result(context, chat_id, user_id, recognize_result, reply_to_message_id)

      context.logger.error(None, extra=dict(
        action="FACEBOOK_RECOGNIZE_TRACK",
        chat_id=chat_id,
        user_id=user_id,
        link=link
      ))
    except:
      context.logger.error(None, extra=dict(
        action="FACEBOOK_RECOGNIZE_TRACK_FAILED",
        chat_id=chat_id,
        user_id=user_id,
        stack_trace=traceback.format_exc(),
        link=link
      ))

async def facebook_handle_link_message(update: Update, context: Context):
  assert update.effective_chat and update.effective_user
  facebook_link = context.matches[0].group(0)

  await required_join_feature_handlers.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, RequiredJoinKind.MEDIA_QUERY)

  if (context.instance.tiktok_quota != -1) and context.instance.tiktok_quota <= context.instance.tiktok_used:
    raise InstanceQuotaLimitReachedException()

  await _facebook_download_telegram(context, facebook_link, update.effective_chat.id, update.effective_user.id, reply_to_message_id=update.effective_message.id)

async def facebook_handle_download_callback_query(update: Update, context: Context):
  assert update.effective_chat and update.effective_user and update.callback_query
  print("salom")
  id = context.matches[0].group(1)
  format_id = context.matches[0].group(2)

  await _facebook_download_telegram(context, update.effective_chat.id, update.effective_user.id, \
      id, format_id, update.effective_message.id)

async def facebook_handle_link_chat_member(update: Update, context: Context, link: str):
  assert update.chat_member and update.effective_user

  await _facebook_download_telegram(context, link, update.effective_user.id, update.effective_user.id)
