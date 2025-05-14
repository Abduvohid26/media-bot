"""add is running column to broadcast table

Revision ID: 52cfade021f0
Revises: 8d04b5a25a8c
Create Date: 2024-06-08 10:46:56.467912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52cfade021f0'
down_revision: Union[str, None] = '8d04b5a25a8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE broadcast ADD COLUMN is_running BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
