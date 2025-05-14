"""add unique constraint on three tables to message seen table

Revision ID: 47ef8b9705e7
Revises: c5f277e1a5fc
Create Date: 2024-07-19 21:18:29.210014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47ef8b9705e7'
down_revision: Union[str, None] = 'c5f277e1a5fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message_seen ADD UNIQUE (message_origin, account_origin, instance_origin);")

def downgrade() -> None:
  pass
