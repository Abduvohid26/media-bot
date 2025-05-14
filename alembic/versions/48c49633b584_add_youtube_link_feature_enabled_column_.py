"""add youtube_link_feature_enabled column to instance table

Revision ID: 48c49633b584
Revises: caf6f2a822e0
Create Date: 2024-11-23 03:43:46.505893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48c49633b584'
down_revision: Union[str, None] = 'caf6f2a822e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  # op.execute("ALTER TABLE instance ADD COLUMN youtube_link_feature_enabled BOOL DEFAULT FALSE;")
  pass


def downgrade() -> None:
    pass
