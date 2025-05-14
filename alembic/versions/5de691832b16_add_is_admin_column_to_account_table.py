"""add is admin column to account table

Revision ID: 5de691832b16
Revises: 6a44aa62a8dc
Create Date: 2024-05-29 22:29:58.392771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5de691832b16'
down_revision: Union[str, None] = '6a44aa62a8dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE account ADD COLUMN is_admin BOOL DEFAULT FALSE;")


def downgrade() -> None:
  op.execute("ALTER TABLE account DROP COLUMN is_admin;")
