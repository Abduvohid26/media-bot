import traceback
from telegram import Update

import mediabot.features.required_join.handlers as required_join_feature_handlers
import mediabot.features.track.handlers as track_feature
from mediabot.exceptions import InstanceQuotaLimitReachedException
from mediabot.context import Context
from mediabot.features.instance.model import Instance
from mediabot.features.required_join.model import RequiredJoinKind
from mediabot.features.tiktok.model import TikTok
from mediabot.features.advertisement.handlers import advertisement_message_send
from mediabot.features.advertisement.model import Advertisement
from mediabot.features.track.model import Track
from mediabot.cache import redis
from mediabot.features.client_manager.manage import ClientManager
from mediabot.features.media_data.model import MediaDataBase
from mediabot.features.centrial_bot.bots.model import CentralBot


async def _tiktok_download_telegram(context: Context, link: str, chat_id: int, user_id: int, reply_to_message_id=None):
    processing_message = None
    should_clear_pending = False

    try:
        try:
            media_file_data, check = await MediaDataBase.get_media_by_link(link, bot_token=context.instance.token)
            if media_file_data:
                if check:
                    await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=media_file_data.get("file_id"))
                    return
                
                channel_id = await CentralBot.get_channel_id()
                message_channel = await context.bot.send_message_video(
                    channel_id, 
                    media_file_data.get("file_id"), 
                    caption=link
                )
                await CentralBot.api_send_external_media(
                    link, 
                    context.instance.token, 
                    context.instance.username, 
                    context.instance.id, 
                    channel_id, 
                    message_channel.message_id
                )
                return
            check_data = await CentralBot.check_main_bot(
                link, 
                context.instance.token, 
                context.instance.username, 
                chat_id
            )
            print(check_data)
            if check_data.get("status"):
                return
        except Exception as e:
           print("error", e)
           pass
            

        if await ClientManager.is_client_pending(user_id):
            await context.bot.send_message(chat_id, context.l("request.pending"), reply_to_message_id=reply_to_message_id)
            return

        processing_message = await context.bot.send_message(
            chat_id,
            context.l("request.processing_text"),
            reply_to_message_id=reply_to_message_id
        )

        file_id_cache = await TikTok.get_tiktok_cache_file_id(context.instance.id, link)

        if file_id_cache:
            sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=file_id_cache)
        else:
            await ClientManager.set_client_pending(user_id)
            should_clear_pending = True  # pending faqat set qilingandan keyin clear qilinadi

            file_id = await TikTok.download_telegram(link, context.instance.token)
            print(file_id, "file id")
            sent_message = await advertisement_message_send(context, chat_id, Advertisement.KIND_VIDEO, video=file_id)
            await TikTok.set_tiktok_cache_file_id(context.instance.id, link, sent_message.video.file_id)
            return
        
        context.logger.info(None, extra=dict(
            action="TIKTOK_DOWNLOAD",
            chat_id=chat_id,
            user_id=user_id,
            link=link
        ))

        await MediaDataBase.add_media_data("tiktok", link, file_id, caption=link, bot_token=context.instance.token, bot_username=context.instance.username)

        await Instance.increment_tiktok_used(context.instance.id)

        if context.instance.tiktok_recognize_track_feature_enabled:
            try:
                recognize_result = await Track.recognize_by_link(link)
                await track_feature.track_recognize_from_recognize_result(context, chat_id, user_id, recognize_result, reply_to_message_id)

                context.logger.info(None, extra=dict(
                    action="TIKTOK_RECOGNIZE_TRACK",
                    chat_id=chat_id,
                    user_id=user_id,
                    link=link
                ))
            except Exception:
                context.logger.error(None, extra=dict(
                    action="TIKTOK_RECOGNIZE_TRACK_FAILED",
                    chat_id=chat_id,
                    user_id=user_id,
                    stack_trace=traceback.format_exc(),
                    link=link
                ))

    except Exception as e:
        print(str(e))
        context.logger.error(None, extra=dict(
            action="TIKTOK_DOWNLOAD_FAILED",
            chat_id=chat_id,
            user_id=user_id,
            link=link,
            stack_trace=traceback.format_exc()
        ))
        await context.bot.send_message(chat_id, context.l("request.failed_text"), reply_to_message_id=reply_to_message_id)

    finally:
        if processing_message:
            await processing_message.delete()
        if should_clear_pending:
            await ClientManager.delete_client_pending(user_id)




async def tiktok_handle_link_message(update: Update, context: Context):
  try:
    assert update.effective_chat and update.effective_user
    tiktok_link = context.matches[0].group(0)

    await required_join_feature_handlers.required_join_handle(context, update.effective_chat.id, \
      update.effective_user.id, RequiredJoinKind.MEDIA_QUERY)

    if (context.instance.tiktok_quota != -1) and context.instance.tiktok_quota <= context.instance.tiktok_used:
      raise InstanceQuotaLimitReachedException()

    await _tiktok_download_telegram(context, tiktok_link, update.effective_chat.id, update.effective_user.id, reply_to_message_id=update.effective_message.id)
  except Exception as e:
    print(traceback.format_exc())
    print(str(e))

async def tiktok_handle_download_callback_query(update: Update, context: Context):
  assert update.effective_chat and update.effective_user and update.callback_query
  id = context.matches[0].group(1)
  format_id = context.matches[0].group(2)

  await _tiktok_download_telegram(context, update.effective_chat.id, update.effective_user.id, \
      id, format_id, update.effective_message.id)

async def tiktok_handle_link_chat_member(update: Update, context: Context, link: str):
  assert update.chat_member and update.effective_user

  await _tiktok_download_telegram(context, link, update.effective_user.id, update.effective_user.id)
