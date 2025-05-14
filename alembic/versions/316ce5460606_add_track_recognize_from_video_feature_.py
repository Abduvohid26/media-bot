"""add_track_recognize_from_video_feature_enabled_column_to_instance_table

Revision ID: 316ce5460606
Revises: b647818e2516
Create Date: 2025-03-10 11:21:38.728489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '316ce5460606'
down_revision: Union[str, None] = 'b647818e2516'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_recognize_from_video_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
