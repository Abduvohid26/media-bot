"""add advertisement_feature_enabled column to instance table

Revision ID: b433e92df897
Revises: 7c45c8805f76
Create Date: 2024-12-19 18:35:56.540724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b433e92df897'
down_revision: Union[str, None] = '7c45c8805f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN advertisement_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
