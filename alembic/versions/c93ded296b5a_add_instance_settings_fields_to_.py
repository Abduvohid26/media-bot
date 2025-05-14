"""add instance settings fields to instance table

Revision ID: c93ded296b5a
Revises: 8f551ccc4341
Create Date: 2024-04-16 16:33:25.285503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c93ded296b5a'
down_revision: Union[str, None] = '8f551ccc4341'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    ALTER TABLE "instance"
    ADD COLUMN "actions_per_second" INTEGER DEFAULT 0,
    ADD COLUMN "track_search_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_download_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "video_search_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "video_download_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_recognize_from_voice_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_recognize_from_audio_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_recognize_from_video_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_recognize_from_youtube_shorts_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_recognize_from_tiktok_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "instagram_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "tiktok_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "youtube_link_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "youtube_link_audio_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "youtube_link_video_feature_enabled" BOOL DEFAULT FALSE,
    ADD COLUMN "track_search_quota" INTEGER DEFAULT 0,
    ADD COLUMN "track_recognize_quota" INTEGER DEFAULT 0,
    ADD COLUMN "track_download_quota" INTEGER DEFAULT 0,
    ADD COLUMN "video_search_quota" INTEGER DEFAULT 0,
    ADD COLUMN "video_download_quota" INTEGER DEFAULT 0,
    ADD COLUMN "instagram_quota" INTEGER DEFAULT 0,
    ADD COLUMN "tiktok_quota" INTEGER DEFAULT 0
  """)


def downgrade() -> None:
  op.execute("""
    ALTER TABLE "instance"
    DROP COLUMN "actions_per_second",
    DROP COLUMN "track_search_feature_enabled",
    DROP COLUMN "track_download_feature_enabled",
    DROP COLUMN "video_search_feature_enabled",
    DROP COLUMN "video_download_feature_enabled",
    DROP COLUMN "track_recognize_from_voice_feature_enabled",
    DROP COLUMN "track_recognize_from_audio_feature_enabled",
    DROP COLUMN "track_recognize_from_video_feature_enabled",
    DROP COLUMN "track_recognize_from_youtube_shorts_feature_enabled",
    DROP COLUMN "track_recognize_from_tiktok_feature_enabled",
    DROP COLUMN "instagram_feature_enabled",
    DROP COLUMN "tiktok_feature_enabled",
    DROP COLUMN "youtube_link_feature_enabled",
    DROP COLUMN "youtube_link_audio_feature_enabled",
    DROP COLUMN "youtube_link_video_feature_enabled",
    DROP COLUMN "track_search_quota",
    DROP COLUMN "track_recognize_quota",
    DROP COLUMN "track_download_quota",
    DROP COLUMN "video_search_quota",
    DROP COLUMN "video_download_quota",
    DROP COLUMN "instagram_quota",
    DROP COLUMN "tiktok_quota"
  """)
