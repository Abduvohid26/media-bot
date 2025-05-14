"""add view count column to required join mark table

Revision ID: 8cd8d6475807
Revises: 6a6c81171ef2
Create Date: 2024-05-08 14:17:08.189446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cd8d6475807'
down_revision: Union[str, None] = '6a6c81171ef2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join_mark ADD COLUMN view_count INTEGER NOT NULL DEFAULT 1")


def downgrade() -> None:
  op.execute("ALTER TABLE required_join_mark DROP COLUMN view_count")
