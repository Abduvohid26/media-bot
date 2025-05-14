"""add is_forward column to message table

Revision ID: c5f277e1a5fc
Revises: 0ef3f9b08017
Create Date: 2024-07-15 22:00:32.117782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5f277e1a5fc'
down_revision: Union[str, None] = '0ef3f9b08017'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN is_forward BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
