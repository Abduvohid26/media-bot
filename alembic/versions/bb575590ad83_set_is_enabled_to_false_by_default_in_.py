"""set is_enabled to false by default in instance table

Revision ID: bb575590ad83
Revises: 8425b10d4524
Create Date: 2024-03-25 22:27:49.592894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb575590ad83'
down_revision: Union[str, None] = '8425b10d4524'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ALTER COLUMN is_enabled SET DEFAULT FALSE;")


def downgrade() -> None:
  op.execute("ALTER TABLE instance ALTER COLUMN is_enabled SET DEFAULT NULL;")