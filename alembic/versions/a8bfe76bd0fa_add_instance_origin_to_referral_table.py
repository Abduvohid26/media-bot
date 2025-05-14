"""add instance origin to referral table

Revision ID: a8bfe76bd0fa
Revises: 1600598b9d9b
Create Date: 2024-04-21 12:11:10.593172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8bfe76bd0fa'
down_revision: Union[str, None] = '1600598b9d9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE referral ADD COLUMN instance_origin INTEGER REFERENCES instance (id) ON DELETE CASCADE")


def downgrade() -> None:
  op.execute("ALTER TABLE referral DROP COLUMN instance_origin")
