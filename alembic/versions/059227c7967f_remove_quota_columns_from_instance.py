"""remove quota columns from instance

Revision ID: 059227c7967f
Revises: 56c00e6c4e51
Create Date: 2024-06-22 17:46:19.528854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '059227c7967f'
down_revision: Union[str, None] = '56c00e6c4e51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN track_search_quota, DROP COLUMN track_recognize_quota, DROP COLUMN track_download_quota, DROP COLUMN video_search_quota, DROP COLUMN video_download_quota, DROP COLUMN instagram_quota, DROP COLUMN tiktok_quota")


def downgrade() -> None:
  pass
