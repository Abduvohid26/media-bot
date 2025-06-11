import traceback
import typing
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message
import time
import re
from mediabot.decorators import check_pending_request
import mediabot.features.required_join.handlers as required_join_feature
from mediabot.exceptions import InstanceQuotaLimitReachedException
from mediabot.features.message.model import Message as MessageModel
from mediabot.context import Context
from mediabot.features.instance.model import Instance
from mediabot.features.advertisement.handlers import advertisement_message_send, Advertisement
from mediabot.features.required_join.model import RequiredJoinKind
from mediabot.features.youtube.buttons import YouTubeSearchDownloadInlineKeyboardMarkup, \
    YouTubeSearchDownloadWebKeyboardMarkup, YouTubeSearchPaginationKeyboardMarkup
from mediabot.features.youtube.model import YouTube
from mediabot.models.request import YouTubeVideoDownloadRequest
from mediabot.features.track.handlers import track_recognize_from_recognize_result
from mediabot.cache import redis
from mediabot.decorators import job_check_youtbe
from mediabot.features.client_manager.manage import ClientManager
from mediabot.features.media_data.model import MediaDataBase
from mediabot.features.centrial_bot.bots.model import CentralBot

YOUTUBE_SEARCH_QUERY_CONTEXT = object()

async def _youtube_search(context: Context, search_query: str, search_page: int, chat_id: int, user_id: int) -> typing.Tuple[str, InlineKeyboardMarkup]:
  try:
    search_results = await YouTube.search(search_query, search_page, 10)

    search_results_text = f"🔍 \"{search_query}\"\n\n"

    for [index, search_result] in enumerate(search_results):
      search_results_text += f"<i><b>{index+1})</b> {search_result['title']} (<u>{time.strftime('%M:%S', time.gmtime(search_result['duration'] or 0))}</u>)</i>\n"

    inline_keyboard_markup = YouTubeSearchDownloadWebKeyboardMarkup.build(search_results, context) \
        if context.instance.web_feature_enabled else YouTubeSearchDownloadInlineKeyboardMarkup.build(search_results)
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard_markup.inline_keyboard + YouTubeSearchPaginationKeyboardMarkup.build(search_page).inline_keyboard)

    # attach advertisements to the search results
    advertisement_messages = await Advertisement.get_all_messages_for(context.instance.id, Advertisement.KIND_YOUTUBE_SEARCH, context.account.id)
    advertisement_attach_messages = [advertisement_message for advertisement_message in advertisement_messages if advertisement_message.is_attach]
    advertisement_attach_message = random.choice(advertisement_attach_messages or [None])
    advertisement_after_messages = [advertisement_message for advertisement_message in advertisement_messages if not advertisement_message.is_attach]

    if advertisement_attach_message:
      deserialized_message = Message.de_json(advertisement_attach_message.message, context.bot)
      assert deserialized_message, "unable to deserialize youtube search advertisement attach message"

      if deserialized_message.text:
        search_results_text += "\n" + deserialized_message.text[:512]
      elif deserialized_message.caption:
        search_results_text += "\n" + deserialized_message.caption[:512]

      if deserialized_message.reply_markup and deserialized_message.reply_markup.inline_keyboard:
        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard_markup.inline_keyboard + deserialized_message.reply_markup.inline_keyboard)

    await Instance.increment_youtube_used(context.instance.id)

    context.logger.info(None, extra=dict(
      action="YOUTUBE_SEARCH",
      search_query=search_query,
      chat_id=chat_id,
      user_id=user_id
    ))

    return (search_results_text, inline_keyboard_markup, advertisement_after_messages)
  except Exception:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="TRACK_SEARCH_FAILED",
      search_query=search_query,
      chat_id=chat_id,
      user_id=user_id,
      stack_trace=traceback.format_exc()
    ))

async def _youtube_link(context: Context, chat_id: int, user_id: int, link: str):
  try:
    video_id_matches = re.findall(r"(youtu.*be.*)\/(watch\?v=|embed\/|v|shorts|)(.*?((?=[&#?])|$))", link)
    video_id = video_id_matches[0][2]
    if "shorts" in link:
      await _youtube_video_download(context, chat_id, user_id, video_id, recognize=True)
    else:
      reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎞 Video", callback_data=f"youtube_video_download_{video_id}"),
        InlineKeyboardButton("🎧 Audio", callback_data=f"track_download_{video_id}")
      ]])

      thumbnails = [
        "sddefault.jpg",
        "hqdefault.jpg",
        "mqdefault.jpg",
        "default.jpg",
      ]

      for thumb in thumbnails:
        url = f"https://i.ytimg.com/vi/{video_id}/{thumb}"
        try:
          await context.bot.send_photo(chat_id, url, reply_markup=reply_markup)
          break
        except Exception as e:
          error_message = str(e)
          if "Wrong type of the web page content" in error_message:
            continue
          else:
            await context.bot.send_message(chat_id, f"❌ Xatolik yuz berdi: {error_message}")
            break
    context.logger.info(None, extra=dict(
      action="YOUTUBE_LINK",
      chat_id=chat_id,
      user_id=user_id,
      link=link
    ))
  except Exception as e:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="YOUTUBE_LINK_FAILED",
      chat_id=chat_id,
      user_id=user_id,
      link=link,
      stack_trace=traceback.format_exc()
    ))





async def _youtube_video_download(context: Context, chat_id: int, user_id: int, id: str, recognize: bool = False, job: str = "job"):
    processing_message = None
    recognize_result = None
    is_pending_set = False

    try:
        try:
            media_file_data, check = await MediaDataBase.get_media_by_link(id, bot_token=context.instance.token)
            if media_file_data:
                if check:
                    print("AQALE")
                    await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=media_file_data.get("file_id"))
                    return
                
                channel_id = await CentralBot.get_channel_id()
                message_channel = await context.bot.send_message_video(
                    channel_id, 
                    media_file_data.get("file_id"), 
                    caption=id
                )
                await CentralBot.api_send_external_media(
                    id, 
                    context.instance.token, 
                    context.instance.username, 
                    context.instance.id, 
                    channel_id, 
                    message_channel.message_id
                )
                return
            check_data = await CentralBot.check_main_bot(
                id, 
                context.instance.token, 
                context.instance.username, 
                chat_id
            )
            if check_data.get("status"):
                return
        except Exception as e:
            print("error", e)
            pass
        file_id = await YouTube.get_youtube_cache_file_id(context.instance.id, id, False)

        if not file_id:
            if await ClientManager.is_client_pending(user_id):
                await context.bot.send_message(chat_id, context.l("request.pending"))
                return

            await ClientManager.set_client_pending(user_id)
            is_pending_set = True

            processing_message = await context.bot.send_message(chat_id, context.l("request.processing_text"))

            file_id, recognize_result = await YouTube.download_telegram(id, context.instance.token, recognize=recognize)

        sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=file_id)

        if recognize_result:
            await track_recognize_from_recognize_result(context, chat_id, user_id, recognize_result)
        await MediaDataBase.add_media_data("youtube", id, sent_message.video.file_id, caption=id, bot_token=context.instance.token, bot_username=context.instance.username)
        await YouTube.set_youtube_cache_file_id(context.instance.id, id, False, sent_message.video.file_id)

    except Exception:
        context.logger.error(None, extra=dict(
            action="YOUTUBE_VIDEO_FAILED",
            chat_id=chat_id,
            user_id=user_id,
            id=id,
            stack_trace=traceback.format_exc()  
        ))
        await context.bot.send_message(chat_id, context.l("request.failed_text"))

    finally:
        if processing_message:
            await processing_message.delete()

        if is_pending_set:
            await ClientManager.delete_client_pending(user_id)

async def youtube_handle_preview_callback_query(update: Update, context: Context):
  assert update.callback_query and update.effective_chat and update.effective_user

  await update.callback_query.answer()

  youtube_video_id = str(context.matches[0].group(1))
  youtube_link = f"https://youtube.com/watch?v={youtube_video_id}"

  await _youtube_link(context, update.effective_chat.id, update.effective_user.id, youtube_link)

async def youtube_handle_link_message(update: Update, context: Context) -> None:
  assert update.message and update.effective_chat.id and update.effective_user.id and update.message.text

  await _youtube_link(context, update.effective_chat.id, update.effective_user.id, update.message.text)

# @check_pending_request(YouTubeVideoDownloadRequest)
async def youtube_handle_video_download_callback_query(update: Update, context: Context):
  assert update.callback_query and update.effective_chat.id and update.effective_user.id

  await update.callback_query.answer()

  id = context.matches[0].group(1)
  
  await _youtube_video_download(context, update.effective_chat.id, update.effective_user.id, id)

async def youtube_handle_video_download_chat_member(update: Update, context: Context, id: str):
  assert update.chat_member

  await _youtube_video_download(context, update.effective_chat.id, update.effective_user.id, id)

async def youtube_handle_search_message(update: Update, context: Context):
  print("Qale")
  assert update.message and update.effective_chat and update.effective_user and context.user_data is not None \
      and update.effective_message and update.effective_message.text

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, required_join_feature.RequiredJoinKind.MEDIA_QUERY)

  if (context.instance.track_quota != -1) and context.instance.track_quota <= context.instance.track_used:
    raise InstanceQuotaLimitReachedException()

  (search_results_text, inline_keyboard_markup, advertisement_after_messages) = await _youtube_search(context, update.effective_message.text, \
      0, update.effective_chat.id, update.effective_user.id)
  await update.message.reply_html(search_results_text, reply_markup=inline_keyboard_markup)

  for advertisement_after_message in advertisement_after_messages:
    deserialized_message = Message.de_json(advertisement_after_message.message, context.bot)
    assert deserialized_message, "unable to deserialize youtube search advertisement after message"
    await MessageModel.send_from_message(update.effective_chat.id, deserialized_message, context.bot)

  context.user_data[YOUTUBE_SEARCH_QUERY_CONTEXT] = update.effective_message.text

async def youtube_handle_search_chat_member(update: Update, context: Context):
  assert update.chat_member
