SELECT
	"instance"."id" AS "instance_id",
	"instance"."token" AS "instance_token",
	"instance"."is_enabled" AS "instance_is_enabled",
	"instance"."created_at" AS "instance_created_at",
	"instance"."base_url" AS "instance_base_url",
	"instance"."username" AS "instance_username",

	"instance"."track_search_feature_enabled" AS "instance_track_search_feature_enabled",
	"instance"."track_download_feature_enabled" AS "instance_track_download_feature_enabled",
	"instance"."track_recognize_from_voice_feature_enabled" AS "instance_track_recognize_from_voice_feature_enabled",
	"instance"."track_recognize_from_video_note_feature_enabled" AS "instance_track_recognize_from_video_note_feature_enabled",
	"instance"."track_recognize_from_audio_feature_enabled" AS "instance_track_recognize_from_audio_feature_enabled",
	"instance"."track_recognize_from_video_feature_enabled" AS "instance_track_recognize_from_video_feature_enabled",
	"instance"."track_quota" AS "instance_track_quota",
	"instance"."track_used" AS "instance_track_used",

	"instance"."instagram_feature_enabled" AS "instance_instagram_feature_enabled",
	"instance"."instagram_recognize_track_feature_enabled" AS "instance_instagram_recognize_track_feature_enabled",
	"instance"."instagram_quota" AS "instance_instagram_quota",
	"instance"."instagram_used" AS "instance_instagram_used",

	"instance"."tiktok_feature_enabled" AS "instance_tiktok_feature_enabled",
	"instance"."tiktok_recognize_track_feature_enabled" AS "instance_tiktok_recognize_track_feature_enabled",
	"instance"."tiktok_quota" AS "instance_tiktok_quota",
	"instance"."tiktok_used" AS "instance_tiktok_used",

	"instance"."twitter_feature_enabled" AS "instance_twitter_feature_enabled",
	"instance"."likee_feature_enabled" AS "instance_likee_feature_enabled",
	"instance"."tumblr_feature_enabled" AS "instance_tumblr_feature_enabled",
	"instance"."pinterest_feature_enabled" AS "instance_pinterest_feature_enabled",
	"instance"."facebook_feature_enabled" AS "instance_facebook_feature_enabled",

	"instance"."youtube_search_feature_enabled" AS "instance_youtube_search_feature_enabled",
	"instance"."youtube_download_feature_enabled" AS "instance_youtube_download_feature_enabled",
	"instance"."youtube_link_feature_enabled" AS "instance_youtube_link_feature_enabled",
	"instance"."youtube_recognize_track_feature_enabled" AS "instance_youtube_recognize_track_feature_enabled",
	"instance"."youtube_quota" AS "instance_youtube_quota",
	"instance"."youtube_used" AS "instance_youtube_used",

	"instance"."broadcast_feature_enabled" AS "instance_broadcast_feature_enabled",
	"instance"."command_feature_enabled" AS "instance_command_feature_enabled",
	"instance"."required_join_feature_enabled" AS "instance_required_join_feature_enabled",
	"instance"."advertisement_feature_enabled" AS "instance_advertisement_feature_enabled",
	"instance"."join_request_feature_enabled" AS "instance_join_request_feature_enabled",
	"instance"."referral_feature_enabled" AS "instance_referral_feature_enabled",

	"instance"."web_feature_enabled" AS "instance_web_feature_enabled",

	"instance"."actions_per_second" AS "instance_actions_per_second"
FROM "instance"
WHERE "instance"."token" = %(token)s;