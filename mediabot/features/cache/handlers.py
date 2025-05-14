from telegram import Update
from mediabot.context import Context
from mediabot.features.track.model import Track
from mediabot.features.youtube.model import YouTube

async def cache_cache_command_handler(update: Update, context: Context) -> None:
  assert update.message

  if not len(context.args) >= 2:
    return

  media_type = str(context.args[0])
  media_id = str(context.args[1])

  file_id = await Track.get_track_cache_file_id(context.instance.id, media_id) \
      if media_type == "track" else await YouTube.get_youtube_cache_file_id(context.instance.id, media_id, False)

  if not file_id:
    return

  if media_type == "track":
    await update.message.reply_audio(file_id)
  else:
    await update.message.reply_video(file_id)
