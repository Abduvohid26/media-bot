"""add required join origin column to message table

Revision ID: 3cc2ca4fef3e
Revises: 1892358e2ad4
Create Date: 2024-04-28 20:00:30.627432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cc2ca4fef3e'
down_revision: Union[str, None] = '1892358e2ad4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN required_join_origin INTEGER REFERENCES required_join (id) ON DELETE CASCADE")


def downgrade() -> None:
  op.execute("ALTER TABLE message DROP COLUMN required_join_origin")
