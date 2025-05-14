"""add is_onetime column to message table

Revision ID: 91a1127cd9b7
Revises: 059227c7967f
Create Date: 2024-07-15 21:21:11.218072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91a1127cd9b7'
down_revision: Union[str, None] = '059227c7967f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN is_onetime BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
