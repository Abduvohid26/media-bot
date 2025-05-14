"""remove old account table

Revision ID: ee608188e44d
Revises: 9e95538a3f5f
Create Date: 2024-03-23 14:41:47.826698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee608188e44d'
down_revision: Union[str, None] = '9e95538a3f5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("DROP TABLE account;")


def downgrade() -> None:
  pass
