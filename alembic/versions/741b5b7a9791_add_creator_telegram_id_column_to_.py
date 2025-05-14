"""add creator telegram id column to instance table

Revision ID: 741b5b7a9791
Revises: fa0d4029100a
Create Date: 2024-06-22 16:45:43.553288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '741b5b7a9791'
down_revision: Union[str, None] = 'fa0d4029100a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN creator_telegram_id BIGINT NOT NULL")


def downgrade() -> None:
  pass
