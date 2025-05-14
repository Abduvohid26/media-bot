"""add track_used column to instance table

Revision ID: 5b6cd9fac734
Revises: d83f8b6ab9af
Create Date: 2024-11-02 11:16:37.598843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b6cd9fac734'
down_revision: Union[str, None] = 'd83f8b6ab9af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_used BIGINT default 0;")


def downgrade() -> None:
  pass
