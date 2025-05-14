"""add schedule count column to required join table

Revision ID: 6a6c81171ef2
Revises: 3cc2ca4fef3e
Create Date: 2024-05-05 12:39:04.920410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a6c81171ef2'
down_revision: Union[str, None] = '3cc2ca4fef3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join ADD COLUMN schedule_count INTEGER DEFAULT 0")


def downgrade() -> None:
  op.execute("ALTER TABLE required_join DROP COLUMN schedule_count")
