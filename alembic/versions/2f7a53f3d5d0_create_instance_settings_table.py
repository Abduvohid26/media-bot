"""create instance settings table

Revision ID: 2f7a53f3d5d0
Revises: 4b07d1a7b6ac
Create Date: 2024-03-25 22:21:51.753035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f7a53f3d5d0'
down_revision: Union[str, None] = '4b07d1a7b6ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "instance_settings" (
      "id" SERIAL PRIMARY KEY,
      "actions_per_second" INTEGER,
      "track_search_feature_enabled" BOOL DEFAULT FALSE,
      "track_download_feature_enabled" BOOL DEFAULT FALSE,
      "video_search_feature_enabled" BOOL DEFAULT FALSE,
      "video_download_feature_enabled" BOOL DEFAULT FALSE,
      "track_recognize_from_voice_feature_enabled" BOOL DEFAULT FALSE,
      "track_recognize_from_audio_feature_enabled" BOOL DEFAULT FALSE,
      "track_recognize_from_video_feature_enabled" BOOL DEFAULT FALSE,
      "track_recognize_from_youtube_shorts_feature_enabled" BOOL DEFAULT FALSE,
      "track_recognize_from_tiktok_feature_enabled" BOOL DEFAULT FALSE,
      "instagram_feature_enabled" BOOL DEFAULT FALSE,
      "tiktok_feature_enabled" BOOL DEFAULT FALSE,
      "youtube_link_feature_enabled" BOOL DEFAULT FALSE,
      "youtube_link_audio_feature_enabled" BOOL DEFAULT FALSE,
      "youtube_link_video_feature_enabled" BOOL DEFAULT FALSE,
      "track_search_quota" INTEGER,
      "track_recognize_quota" INTEGER,
      "track_download_quota" INTEGER,
      "video_search_quota" INTEGER,
      "video_download_quota" INTEGER,
      "instagram_quota" INTEGER,
      "tiktok_quota" INTEGER,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE instance_settings;")
