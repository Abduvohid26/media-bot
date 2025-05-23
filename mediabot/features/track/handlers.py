import time
import typing
import traceback

from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultArticle, InputTextMessageContent, InputMediaAudio
from telegram.ext import ApplicationHandlerStop

import mediabot.features.required_join.handlers as required_join_feature
from mediabot.context import Context
from mediabot.features.instance.model import Instance
from mediabot.features.advertisement.model import Advertisement
from mediabot.features.language.model import Language
from mediabot.features.required_join.model import RequiredJoinKind
from mediabot.features.track.model import TRACK_SEARCH_QUERY_CONTEXT, Track
from mediabot.features.track.buttons import TrackSearchDownloadInlineKeyboardMarkup, \
    TrackSearchDownloadWebKeyboardMarkup, TrackSearchPaginationKeyboardMarkup
from mediabot.features.track.constants import TRACK_SEARCH_LIMIT
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.exceptions import InstanceQuotaLimitReachedException
from mediabot.utils import get_local_path_of

async def _track_search(context: Context, search_query: str, search_page: int, chat_id: int, user_id: int) -> typing.Tuple[str, InlineKeyboardMarkup]:
  try:
    search_results = await Track.search(search_query, search_page, TRACK_SEARCH_LIMIT)
    search_results_text = f"🔍 \"{search_query}\"\n\n"

    for [index, search_result] in enumerate(search_results):
      search_results_text += f"<i><b>{index+1})</b> {search_result['title']} (<u>{time.strftime('%M:%S', time.gmtime(search_result['duration'] or 0))}</u>)</i>\n"

    reply_markup = TrackSearchDownloadWebKeyboardMarkup.build(search_results, context) \
        if context.instance.web_feature_enabled else TrackSearchDownloadInlineKeyboardMarkup.build(search_results)
    reply_markup = InlineKeyboardMarkup(reply_markup.inline_keyboard + TrackSearchPaginationKeyboardMarkup.build(search_page).inline_keyboard)

    context.logger.info(None, extra=dict(
      action="TRACK_SEARCH",
      search_query=search_query,
      chat_id=chat_id,
      user_id=user_id
    ))

    return (search_results_text, reply_markup)
  except Exception as ex:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="TRACK_SEARCH_FAILED",
      search_query=search_query,
      chat_id=chat_id,
      user_id=user_id,
      stack_trace=traceback.format_exc()
    ))

    raise ApplicationHandlerStop()

async def _track_download(context: Context, track_id: str, chat_id: int, user_id: int) -> None:
  processing_text = await context.bot.send_message(chat_id, context.l("request.processing_text"))

  try:
    track_file_id = await Track.get_track_cache_file_id(context.instance.id, track_id)

    if not track_file_id:
      track_file_id = await Track.download_telegram(track_id, context.instance.token, context.instance.username)
  
    sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_AUDIO, audio=track_file_id)
    await Track.set_track_cache_file_id(context.instance.id, track_id, sent_message.audio.file_id)

    await Instance.increment_track_used(context.instance.id)

    context.logger.info(None, extra=dict(
      action="TRACK_DOWNLOAD",
      track_id=track_id,
      chat_id=chat_id,
      user_id=user_id
    ))

  except Exception:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="TRACK_DOWNLOAD_FAILED",
      track_id=track_id,
      chat_id=chat_id,
      user_id=user_id,
      stack_trace=traceback.format_exc()
    ))
  finally:
    await processing_text.delete()

async def track_handle_search_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and update.callback_query.data and context.matches and update.effective_chat \
      and update.effective_user and update.effective_message and context.user_data is not None

  await update.callback_query.answer()

  if TRACK_SEARCH_QUERY_CONTEXT not in context.user_data:
    return await update.effective_message.delete()

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, RequiredJoinKind.MEDIA_QUERY)

  if (context.instance.track_quota != -1) and context.instance.track_quota <= context.instance.track_used:
    raise InstanceQuotaLimitReachedException()

  search_query = str(context.user_data.get(TRACK_SEARCH_QUERY_CONTEXT, ""))
  search_page = int(context.matches[0].groups(0)[0])

  (search_results_text, inline_keyboard_markup) = await _track_search(context, search_query, \
      search_page, update.effective_chat.id, update.effective_user.id)

  await update.effective_message.edit_text(search_results_text, reply_markup=inline_keyboard_markup)

async def track_handle_search_message(update: Update, context: Context) -> None:
  assert update.message and update.effective_chat and update.effective_user and context.user_data is not None \
      and update.effective_message and update.effective_message.text

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, RequiredJoinKind.MEDIA_QUERY)

  if (context.instance.track_quota != -1) and context.instance.track_quota <= context.instance.track_used:
    raise InstanceQuotaLimitReachedException()

  search_query = update.effective_message.text
  search_page = 0

  (search_results_text, reply_markup) = await _track_search(context, search_query, \
      search_page, update.effective_chat.id, update.effective_user.id)

  await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_TRACK_SEARCH, \
      text=search_results_text, reply_markup=reply_markup, reply_to_message_id=update.message.id)

  context.user_data[TRACK_SEARCH_QUERY_CONTEXT] = search_query

async def track_handle_search_chat_member(update: Update, context: Context, search_query: str) -> None:
  assert update.chat_member and context.user_data is not None

  search_page = 0

  (search_results_text, inline_keyboard_markup,) = await _track_search(context, search_query, \
      search_page, update.chat_member.from_user.id, update.chat_member.from_user.id)

  await context.bot.send_message(update.chat_member.from_user.id, \
      search_results_text, reply_markup=inline_keyboard_markup)

  context.user_data[TRACK_SEARCH_QUERY_CONTEXT] = search_query

# @check_pending_request(TrackDownloadRequest)
async def track_handle_download_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query and update.effective_message and context.user_data is not None and context.matches and update.effective_user and update.effective_chat

  await update.callback_query.answer()

  track_id = str(context.matches[0].groups(0)[0])
  print(track_id, "ID")

  await required_join_feature.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, RequiredJoinKind.MEDIA_DOWNLOAD)

  if (context.instance.track_quota != -1) and context.instance.track_quota <= context.instance.track_used:
    raise InstanceQuotaLimitReachedException()

  await _track_download(context, track_id, update.effective_chat.id, update.effective_user.id)

async def track_handle_download_chat_member(update: Update, context: Context, track_id: str) -> None:
  assert update.chat_member

  await _track_download(context, track_id, update.chat_member.from_user.id, update.chat_member.from_user.id)

async def track_handle_download_web(context: Context, chat_id: int, user_id: int, track_id: str) -> None:
  await _track_download(context, track_id, chat_id, user_id)

async def _track_popular(context: Context, country_code: str, page: int = 0) -> None:
  languages = await Language.get_all(context.instance.id)

  popular_tracks = await Track.get_popular_tracks(country_code, offset=page, limit=10)

  popular_tracks_text = "<b>Popular tracks:</b>\n\n"

  for index, track in enumerate(popular_tracks):
    popular_tracks_text += f"<b>{index+1}</b>) <i>{track['title']}</i> (<u>{time.strftime('%M:%S', time.gmtime(track['duration'] or 0))}</u>)\n"

  track_buttons = [
    [InlineKeyboardButton("🎵 " + str(outer*5+inner+1), callback_data=f"track_download_{popular_tracks[outer*5+inner]['id']}")
      for inner in range(min(5, len(popular_tracks) - (outer*5)))] for outer in range(max(len(popular_tracks), round(len(popular_tracks) / 5)))
  ]

  language_buttons = [
    [InlineKeyboardButton(languages[outer*3+inner].name, callback_data=f"popular_tracks_country_code_{languages[outer*3+inner].code.upper()}")
      for inner in range(min(3, len(languages) - (outer*3)))] for outer in range(max(len(languages), round(len(languages) / 3)))
  ]

  pagination_buttons = [
    [InlineKeyboardButton("➡️", callback_data="popular_tracks_next")],
  ]

  if page != 0:
    pagination_buttons[0].insert(0, InlineKeyboardButton("⬅️", callback_data="popular_tracks_previous"))

  reply_markup = InlineKeyboardMarkup(track_buttons + language_buttons + pagination_buttons)

  return (popular_tracks_text, reply_markup,)

async def track_handle_popular_tracks_command(update: Update, context: Context) -> None:
  assert update.effective_message

  context.user_data["popular_tracks_page"] = 0
  context.user_data["popular_tracks_country_code"] = (context.account.language.code if context.account.language else "us").upper()

  (popular_tracks_text, reply_markup) = await _track_popular(context, context.user_data["popular_tracks_country_code"], int(context.user_data["popular_tracks_page"]))

  await update.effective_message.reply_text(popular_tracks_text, reply_markup=reply_markup)

async def track_handle_popular_tracks_previous_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()
  country_code = context.user_data.setdefault("popular_tracks_country_code", "US")
  context.user_data["popular_tracks_page"] = context.user_data.get("popular_tracks_page", 0) - 10

  (popular_tracks_text, reply_markup) = await _track_popular(context, country_code, context.user_data["popular_tracks_page"])

  await update.callback_query.edit_message_text(popular_tracks_text, reply_markup=reply_markup)

async def track_handle_popular_tracks_next_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()
  country_code = context.user_data.setdefault("popular_tracks_country_code", "US")

  context.user_data["popular_tracks_page"] = context.user_data.get("popular_tracks_page", 0) + 10

  (popular_tracks_text, reply_markup) = await _track_popular(context, country_code, context.user_data["popular_tracks_page"])

  await update.callback_query.edit_message_text(popular_tracks_text, reply_markup=reply_markup)

async def track_handle_popular_tracks_country_code_callback_query(update: Update, context: Context) -> None:
  assert update.callback_query

  await update.callback_query.answer()

  country_code = str(context.matches[0].groups(0)[0])
  context.user_data["popular_tracks_country_code"] = country_code

  (popular_tracks_text, reply_markup) = await _track_popular(context, country_code, context.user_data.get("popular_tracks_page", 0))

  await update.callback_query.edit_message_text(popular_tracks_text, reply_markup=reply_markup)

async def track_recognize_by_file_path(context: Context, chat_id: int, user_id: int, file_path: str, reply_message_id: int = None):
  try:
    recognize_result = await Track.recognize_by_file_path(file_path)

    await track_recognize_from_recognize_result(context, chat_id, user_id, recognize_result, reply_message_id)
  except Exception:
    await context.bot.send_message(chat_id, context.l("request.failed_text"))

    context.logger.error(None, extra=dict(
      action="TRACK_RECOGNIZE_FAILED",
      chat_id=chat_id,
      user_id=user_id,
      file_path=file_path,
      stack_trace=traceback.format_exc()
    ))

    return

  context.logger.info(None, extra=dict(
    action="TRACK_RECOGNIZE",
    chat_id=chat_id,
    user_id=user_id,
    file_path=file_path
  ))

async def track_handle_recognize_from_voice_message(update: Update, context: Context):
  assert update.message and update.message.voice

  # TODO: add required join

  if update.message.voice.file_size >= 31457280:
    await update.message.reply_text(context.l("request.file_is_too_big_text"))
    return

  voice_file = await update.message.voice.get_file()
  local_voice_file_path = get_local_path_of(voice_file)

  await track_recognize_by_file_path(context, update.effective_message.chat.id, \
      update.effective_user.id, local_voice_file_path, update.effective_message.id)

  Path(local_voice_file_path).unlink(missing_ok=True)

async def track_handle_recognize_from_video_note_message(update: Update, context: Context):
  assert update.message and update.message.video_note

  if update.message.video_note.file_size >= 31457280:
    await update.message.reply_text(context.l("request.file_is_too_big_text"))
    return

  video_note_file = await update.message.video_note.get_file()
  local_video_note_file_path = get_local_path_of(video_note_file)

  await track_recognize_by_file_path(context, update.effective_message.chat.id, \
      update.effective_user.id, local_video_note_file_path, update.effective_message.id)

  Path(local_video_note_file_path).unlink(missing_ok=True)

async def track_handle_recognize_from_video_message(update: Update, context: Context):
  assert update.message and update.message.video

  if update.message.video.file_size >= 31457280:
    await update.message.reply_text(context.l("request.file_is_too_big_text"))
    return

  video_message = await update.message.video.get_file()
  local_video_file_path = get_local_path_of(video_message)

  await track_recognize_by_file_path(context, update.effective_message.chat.id, \
      update.effective_user.id, local_video_file_path, update.effective_message.id)

  Path(local_video_file_path).unlink(missing_ok=True)

async def track_handle_recognize_from_audio_message(update: Update, context: Context):
  assert update.message and update.message.audio

  if update.message.audio.file_size >= 31457280:
    await update.message.reply_text(context.l("request.file_is_too_big_text"))
    return

  audio_file = await update.message.audio.get_file()
  local_audio_file_path = get_local_path_of(audio_file)

  await track_recognize_by_file_path(context, update.effective_message.chat.id, \
      update.effective_user.id, local_audio_file_path, update.effective_message.id)

  Path(local_audio_file_path).unlink(missing_ok=True)

async def track_recognize_from_recognize_result(context: Context, chat_id: int, user_id: int, recognize_result: dict, reply_to_message_id: int = None):
  recognize_text = f"<b>{recognize_result['title']}</b> - <b>{recognize_result['performer']}</b>"
  try:
    await context.bot.send_photo(chat_id, recognize_result['thumbnail_url'], \
        caption=recognize_text, reply_to_message_id=reply_to_message_id)
  except:
    await context.bot.send_message(chat_id, recognize_text, reply_to_message_id=reply_to_message_id)

  search_query = f"{recognize_result['title']} {recognize_result['performer']}"
  (search_results_text, inline_keyboard_markup) = await _track_search(context, search_query, 0, chat_id, user_id)

  await context.bot.send_message(chat_id, search_results_text, \
      reply_markup=inline_keyboard_markup, reply_to_message_id=reply_to_message_id)

async def track_group_search_command(update: Update, context: Context):
  if (context.instance.track_quota != -1) and context.instance.track_quota <= context.instance.track_used:
    raise InstanceQuotaLimitReachedException()

  search_query = context.args[0] if len(context.args) > 0 else update.effective_message.text
  search_page = 0

  (search_results_text, reply_markup) = await _track_search(context, search_query, \
      search_page, update.effective_chat.id, update.effective_user.id)

  await update.effective_message.reply_text(search_results_text, reply_markup=reply_markup)

  context.user_data[TRACK_SEARCH_QUERY_CONTEXT] = search_query

async def track_search_inline_query_handler(update: Update, context: Context):
  assert update.inline_query

  search_results = await Track.search(update.inline_query.query, 0, 32)

  inline_keyboard_markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"{context.bot.name}", url=f"https://t.me/{context.instance.username}")]])

  search_results_articles = [
    InlineQueryResultArticle(
      id=search_result['id'],
      title=search_result['title'],
      description=f"🎤 {search_result['performer']}, 🕒 {time.strftime('%M:%S', time.gmtime(search_result['duration'] or 0))}",
      input_message_content=InputTextMessageContent(f"🎵 {search_result['title']} ..."),
      thumbnail_url=search_result['thumbnail_url'],
      reply_markup=inline_keyboard_markup,
      thumbnail_width=100,
      thumbnail_height=100,
    ) for search_result in search_results]

  await update.inline_query.answer(search_results_articles)

async def track_chosen_inline_query_handler(update: Update, context: Context):
  assert update.chosen_inline_result

  try:
    track_file_id = await Track.get_track_cache_file_id(context.instance.id, update.chosen_inline_result.result_id)

    if not track_file_id:
      track_file_id = await Track.download_telegram(update.chosen_inline_result.result_id, context.instance.token, context.instance.username)

    sent_message = await context.bot.edit_message_media(InputMediaAudio(track_file_id), inline_message_id=update.chosen_inline_result.inline_message_id)
    await Track.set_track_cache_file_id(context.instance.id, update.chosen_inline_result.result_id, sent_message.audio.file_id)

    await Instance.increment_track_used(context.instance.id)
  except Exception:
    pass
