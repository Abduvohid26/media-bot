"""add youtube_used column to instance table

Revision ID: caf6f2a822e0
Revises: 6e7fc164263e
Create Date: 2024-11-23 03:34:47.177642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caf6f2a822e0'
down_revision: Union[str, None] = '6e7fc164263e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN youtube_used BIGINT DEFAULT 0")


def downgrade() -> None:
  pass
