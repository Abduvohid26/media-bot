"""add username column to instance table

Revision ID: 0f20042e7536
Revises: cc5b114ddb23
Create Date: 2024-05-28 22:20:04.372800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f20042e7536'
down_revision: Union[str, None] = 'cc5b114ddb23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  # op.execute("ALTER TABLE instance ADD COLUMN username VARCHAR NOT NULL;")
  pass


def downgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN username;")
