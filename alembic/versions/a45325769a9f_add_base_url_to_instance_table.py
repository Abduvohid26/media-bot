"""add base_url to instance table

Revision ID: a45325769a9f
Revises: c93ded296b5a
Create Date: 2024-04-16 17:45:38.594287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a45325769a9f'
down_revision: Union[str, None] = 'c93ded296b5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN base_url VARCHAR DEFAULT NULL");


def downgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN base_url");
