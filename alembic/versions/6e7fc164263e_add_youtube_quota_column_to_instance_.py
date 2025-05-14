"""add youtube_quota column to instance table

Revision ID: 6e7fc164263e
Revises: 534ecf196ddc
Create Date: 2024-11-23 03:34:04.671642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e7fc164263e'
down_revision: Union[str, None] = '534ecf196ddc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN youtube_quota BIGINT DEFAULT -1")


def downgrade() -> None:
  pass
