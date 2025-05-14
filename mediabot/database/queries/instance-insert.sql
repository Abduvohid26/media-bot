INSERT INTO "instance" (
  "token",
  "username",
  "track_feature_enabled",
  "track_recognize_from_voice_feature_enabled",
  "track_recognize_from_audio_feature_enabled",
  "track_recognize_from_video_note_feature_enabled",
  "track_quota",

  "instagram_feature_enabled",
  "instagram_recognize_track_feature_enabled",
  "instagram_quota",

  "tiktok_feature_enabled",
  "tiktok_recognize_track_feature_enabled",
  "tiktok_quota",

  "youtube_feature_enabled",
  "youtube_recognize_track_feature_enabled",
  "youtube_quota",

  "broadcast_feature_enabled",
  "command_feature_enabled",
  "required_join_feature_enabled",
  "advertisement_feature_enabled",
  "referral_feature_enabled",
  "join_request_feature_enabled",

  "web_feature_enabled"
)
VALUES (
  %(token)s,
  %(username)s,
  %(track_feature_enabled)s,
  %(track_recognize_from_voice_feature_enabled)s,
  %(track_recognize_from_audio_feature_enabled)s,
  %(track_recognize_from_video_note_feature_enabled)s,
  %(track_quota)s,

  %(instagram_feature_enabled)s,
  %(instagram_recognize_track_feature_enabled)s,
  %(instagram_quota)s,

  %(tiktok_feature_enabled)s,
  %(tiktok_recognize_track_feature_enabled)s,
  %(tiktok_quota)s,

  %(youtube_feature_enabled)s,
  %(youtube_recognize_track_feature_enabled)s,
  %(youtube_quota)s,

  %(broadcast_feature_enabled)s,
  %(command_feature_enabled)s,
  %(required_join_feature_enabled)s,
  %(advertisement_feature_enabled)s,
  %(referral_feature_enabled)s,
  %(join_request_feature_enabled)s,

  %(web_feature_enabled)s
)
RETURNING "id";
