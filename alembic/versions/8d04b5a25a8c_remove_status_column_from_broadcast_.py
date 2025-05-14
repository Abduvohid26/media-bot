"""remove status column from broadcast table

Revision ID: 8d04b5a25a8c
Revises: 408eca0cd325
Create Date: 2024-06-08 10:46:16.259403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d04b5a25a8c'
down_revision: Union[str, None] = '408eca0cd325'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE broadcast DROP COLUMN status;")


def downgrade() -> None:
  pass
