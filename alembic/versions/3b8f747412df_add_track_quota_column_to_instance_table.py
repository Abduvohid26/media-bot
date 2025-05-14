"""add track_quota column to instance table

Revision ID: 3b8f747412df
Revises: 84613e19fb43
Create Date: 2024-11-02 08:57:04.738888

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b8f747412df'
down_revision: Union[str, None] = '84613e19fb43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_quota BIGINT DEFAULT -1")


def downgrade() -> None:
  pass
