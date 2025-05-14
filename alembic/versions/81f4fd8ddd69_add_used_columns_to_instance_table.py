"""add_used_columns_to_instance_table

Revision ID: 81f4fd8ddd69
Revises: c128f97e6058
Create Date: 2024-09-04 16:58:50.003953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81f4fd8ddd69'
down_revision: Union[str, None] = 'c128f97e6058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    ALTER TABLE instance ADD COLUMN track_download_used INTEGER DEFAULT 0,
        ADD COLUMN video_download_used INTEGER DEFAULT 0,
        ADD COLUMN video_search_used INTEGER DEFAULT 0,
        ADD COLUMN instagram_used INTEGER DEFAULT 0,
        ADD COLUMN tiktok_used INTEGER DEFAULT 0;
  """)

def downgrade() -> None:
    pass
