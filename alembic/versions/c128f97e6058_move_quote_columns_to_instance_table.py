"""move quote columns to instance table

Revision ID: c128f97e6058
Revises: f10b634032bf
Create Date: 2024-09-04 16:29:26.075279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c128f97e6058'
down_revision: Union[str, None] = 'f10b634032bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
      "track_search_quota": track_search_quota,
      "track_download_quota": track_download_quota,
      "video_search_quota": video_search_quota,
      "video_download_quota": video_download_quota,
      "instagram_quota": instagram_quota,
      "tiktok_quota": tiktok_quota
"""

def upgrade() -> None:
  op.execute("DROP TABLE instance_quota;")
  op.execute("""
    ALTER TABLE instance ADD COLUMN track_search_quota INTEGER DEFAULT -1,
        ADD COLUMN track_download_quota INTEGER NOT NULL DEFAULT -1,
        ADD COLUMN video_search_quota INTEGER NOT NULL DEFAULT -1,
        ADD COLUMN video_download_quota INTEGER NOT NULL DEFAULT -1,
        ADD COLUMN instagram_quota INTEGER NOT NULL DEFAULT -1,
        ADD COLUMN tiktok_quota INTEGER NOT NULL DEFAULT -1;
  """)


def downgrade() -> None:
  pass
