"""remove username column from instance table

Revision ID: 8425b10d4524
Revises: 2f7a53f3d5d0
Create Date: 2024-03-25 22:23:55.539719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8425b10d4524'
down_revision: Union[str, None] = '2f7a53f3d5d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN username;")


def downgrade() -> None:
  pass
