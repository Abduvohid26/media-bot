from telegram.ext import filters, Application, MessageHandler, CallbackQueryHandler, CommandHandler, InlineQueryHandler, ChosenInlineResultHandler

from mediabot.features.track.handlers import track_group_search_command, track_handle_download_callback_query, track_handle_popular_tracks_command, \
    track_handle_popular_tracks_country_code_callback_query, track_handle_recognize_from_video_note_message, track_handle_recognize_from_voice_message, \
    track_handle_search_message, track_handle_search_callback_query, track_handle_recognize_from_video_message, track_handle_recognize_from_audio_message, \
    track_search_inline_query_handler, track_chosen_inline_query_handler, track_handle_popular_tracks_previous_callback_query, track_handle_popular_tracks_next_callback_query

class TrackSearchFeature:
  track_search_message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE, track_handle_search_message)
  track_group_search_command_handler = CommandHandler("search", track_group_search_command, filters.ChatType.GROUPS)
  track_search_previous_callback_query_handler = CallbackQueryHandler(track_handle_search_callback_query, "^track_search_previous_([0-9]+)$")
  track_search_next_callback_query_handler = CallbackQueryHandler(track_handle_search_callback_query, "^track_search_next_([0-9]+)$")
  track_search_inline_query_handler = InlineQueryHandler(track_search_inline_query_handler)
  track_chosen_inline_query_handler = ChosenInlineResultHandler(track_chosen_inline_query_handler)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackSearchFeature.track_search_message_handler)
    botapp.add_handler(TrackSearchFeature.track_search_previous_callback_query_handler)
    botapp.add_handler(TrackSearchFeature.track_search_next_callback_query_handler)
    botapp.add_handler(TrackSearchFeature.track_group_search_command_handler)
    botapp.add_handler(TrackSearchFeature.track_search_inline_query_handler, group=-99)
    botapp.add_handler(TrackSearchFeature.track_chosen_inline_query_handler, group=-99)

class TrackDownloadFeature:
  track_download_callback_query_handler = CallbackQueryHandler(track_handle_download_callback_query, "^track_download_([:a-zA-Z0-9_-]+)$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackDownloadFeature.track_download_callback_query_handler)

class TrackPopularTracksFeature:
  track_popular_tracks_command_handler = CommandHandler("popular_tracks", track_handle_popular_tracks_command)
  track_popular_tracks_callback_query_handler = CallbackQueryHandler(track_handle_popular_tracks_country_code_callback_query, "^popular_tracks_country_code_([a-zA-Z]+)$")
  track_popular_tracks_previous_callback_query_handler = CallbackQueryHandler(track_handle_popular_tracks_previous_callback_query, "^popular_tracks_previous$")
  track_popular_tracks_next_callback_query_handler = CallbackQueryHandler(track_handle_popular_tracks_next_callback_query, "^popular_tracks_next$")

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackPopularTracksFeature.track_popular_tracks_command_handler)
    botapp.add_handler(TrackPopularTracksFeature.track_popular_tracks_previous_callback_query_handler)
    botapp.add_handler(TrackPopularTracksFeature.track_popular_tracks_next_callback_query_handler)
    botapp.add_handler(TrackPopularTracksFeature.track_popular_tracks_callback_query_handler)

class TrackRecognizeFromVoiceFeature:
  track_voice_message_handler = MessageHandler(filters.VOICE & filters.ChatType.PRIVATE, track_handle_recognize_from_voice_message)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackRecognizeFromVoiceFeature.track_voice_message_handler)

class TrackRecognizeFromVideoNoteFeature:
  track_video_note_message_handler = MessageHandler(filters.VIDEO_NOTE & filters.ChatType.PRIVATE, track_handle_recognize_from_video_note_message)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackRecognizeFromVideoNoteFeature.track_video_note_message_handler)

class TrackRecognizeFromVideoFeature:
  track_video_message_handler = MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, track_handle_recognize_from_video_message)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackRecognizeFromVideoFeature.track_video_message_handler)

class TrackRecognizeFromAudioFeature:
  track_audio_message_handler = MessageHandler(filters.AUDIO & filters.ChatType.PRIVATE, track_handle_recognize_from_audio_message)

  @staticmethod
  def register_handlers(botapp: Application):
    botapp.add_handler(TrackRecognizeFromAudioFeature.track_audio_message_handler)
