"""add required_join_feature_enabled column to instance table

Revision ID: 7c45c8805f76
Revises: bd498c527704
Create Date: 2024-12-19 18:34:14.120694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c45c8805f76'
down_revision: Union[str, None] = 'bd498c527704'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN required_join_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
    pass
