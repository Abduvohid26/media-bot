"""remove unecessary instance columns

Revision ID: 56c00e6c4e51
Revises: 741b5b7a9791
Create Date: 2024-06-22 17:03:08.871224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56c00e6c4e51'
down_revision: Union[str, None] = '741b5b7a9791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN actions_per_second, DROP COLUMN track_recognize_from_voice_feature_enabled, DROP COLUMN track_recognize_from_audio_feature_enabled, DROP COLUMN track_recognize_from_video_feature_enabled, DROP COLUMN track_recognize_from_youtube_shorts_feature_enabled, DROP COLUMN track_recognize_from_tiktok_feature_enabled")


def downgrade() -> None:
  pass
