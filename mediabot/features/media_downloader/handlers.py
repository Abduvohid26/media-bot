import traceback
import pathlib
import mediabot.features.required_join.handlers as required_join_feature_handlers
from telegram import Update
from mediabot.context import Context
from mediabot.features.media_downloader.model import MediaService
from mediabot.features.media_downloader.buttons import MediaDownloaderCollectionKeyboardMarkup
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.features.advertisement.model import Advertisement
from mediabot.utils import AsyncFileDownloader

async def media_downloader_handle_link_message(update: Update, context: Context):
  assert update.effective_message

  await required_join_feature_handlers.required_join_handle(context, update.effective_chat.id, \
    update.effective_user.id, required_join_feature_handlers.RequiredJoinKind.MEDIA_QUERY)

  processing_message = await context.bot.send_message(update.effective_chat.id, \
      context.l("request.processing_text"), reply_to_message_id=update.effective_message.id)

  # pseudo-global variable so when everything goes wrong after download we can "unlink" the file
  downloaded_media_path = None

  try:
    info = await MediaService.info(update.effective_message.text)

    if info["type"] == "collection":
      link_info_id = await MediaService.save_link_info(info)
      reply_markup = MediaDownloaderCollectionKeyboardMarkup.build(info["collection"], link_info_id)
      first_photo_collection_item = filter(lambda coll: coll["type"] == "photo", info["collection"])

      if any(first_photo_collection_item):
        photo_collection_item = next(first_photo_collection_item)
        photo_url_to_send = photo_collection_item["thumbnail_url"] or photo_collection_item["download_url"]
        await update.effective_message.reply_photo(photo=photo_url_to_send, reply_markup=reply_markup)
      else:
        await update.effective_message.reply_text(update.effective_message.text, reply_markup=reply_markup)

      return

    if info["type"] == "photo":
      return await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_PHOTO, \
          photo=info["download_url"], reply_to_message_id=update.effective_message.id)

    downloaded_media_path = await AsyncFileDownloader.download_file_to_local(info["download_url"])

    with open(downloaded_media_path, "rb") as fd:
      await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_VIDEO, video=fd)

  except Exception:
    await context.bot.send_message(
      update.effective_chat.id,
      context.l("request.failed_text"),
      reply_to_message_id=update.effective_message.id
    )

    context.logger.error(None, extra=dict(
      action="MEDIA_LINK_FAILED",
      chat_id=update.effective_chat.id,
      user_id=update.effective_user.id,
      link=update.effective_message.id,
      stack_trace=traceback.format_exc()
    ))
  finally:
    await processing_message.delete()

    if downloaded_media_path:
      pathlib.Path(downloaded_media_path).unlink(missing_ok=True)

async def media_downloader_handle_download_callback_query(update: Update, context: Context):
  assert update.callback_query

  processing_message = await context.bot.send_message(update.effective_chat.id, \
      context.l("request.processing_text"), reply_to_message_id=update.effective_message.id)

  link_info_id = context.matches[0].group(1)
  link_info_collection_index = int(context.matches[0].group(2))

  downloaded_media_path = None

  try:
    link_info = await MediaService.get_link_info(link_info_id)

    link_info_collection_item = link_info["collection"][link_info_collection_index]

    if link_info_collection_item["type"] == "photo":
      return await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_PHOTO, \
        photo=link_info_collection_item["download_url"], reply_to_message_id=update.effective_message.id)

    downloaded_media_path = await AsyncFileDownloader.download_file_to_local(link_info_collection_item["download_url"])
    with open(downloaded_media_path, "rb") as fd:
      await advertisement_message_send(context, update.effective_chat.id, Advertisement.KIND_VIDEO, video=fd)
  except:
    await context.bot.send_message(
      update.effective_chat.id,
      context.l("request.failed_text"),
      reply_to_message_id=update.effective_message.id
    )
    
    context.logger.error(None, extra=dict(
      action="MEDIA_DOWNLOAD_FAILED",
      chat_id=update.effective_chat.id,
      user_id=update.effective_user.id,
      stack_trace=traceback.format_exc()
    ))
  finally:
    await processing_message.delete()
    if downloaded_media_path:
      pathlib.Path(downloaded_media_path).unlink(missing_ok=True)