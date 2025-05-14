"""add is attach column to message table

Revision ID: fa0d4029100a
Revises: 3aa5e35368f2
Create Date: 2024-06-18 14:02:05.367234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa0d4029100a'
down_revision: Union[str, None] = '3aa5e35368f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN is_attach BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
