"""add is after join column to message table

Revision ID: f10b634032bf
Revises: 3cc4f720f481
Create Date: 2024-07-30 22:22:55.851790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f10b634032bf'
down_revision: Union[str, None] = '3cc4f720f481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN is_after_join BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
