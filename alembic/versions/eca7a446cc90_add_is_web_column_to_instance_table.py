"""add is web column to instance table

Revision ID: eca7a446cc90
Revises: f5e45ba9de5f
Create Date: 2024-07-28 08:15:34.305383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca7a446cc90'
down_revision: Union[str, None] = 'f5e45ba9de5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN is_web BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
