"""add youtube_recognize_track_feature_enabled column to instance table

Revision ID: 326650e8caf2
Revises: 1c83e1e8dffa
Create Date: 2024-12-19 18:16:08.942794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '326650e8caf2'
down_revision: Union[str, None] = '1c83e1e8dffa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN youtube_recognize_track_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
