"""add join_request_feature_enabled column to instance table

Revision ID: 5b983a323a26
Revises: b433e92df897
Create Date: 2024-12-19 18:36:49.048382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b983a323a26'
down_revision: Union[str, None] = 'b433e92df897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  # op.execute("ALTER TABLE instance ADD COLUMN join_request_feature_enabled BOOL DEFAULT FALSE")
  pass


def downgrade() -> None:
  pass
