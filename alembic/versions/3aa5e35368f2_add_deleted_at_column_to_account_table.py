"""add deleted at column to account table

Revision ID: 3aa5e35368f2
Revises: 72dc3bb48fb5
Create Date: 2024-06-14 16:06:38.414733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3aa5e35368f2'
down_revision: Union[str, None] = '72dc3bb48fb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE account ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL")


def downgrade() -> None:
  pass
