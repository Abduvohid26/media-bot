"""add command_feature_enabled column to instance table

Revision ID: bd498c527704
Revises: ebfdf80d2ddb
Create Date: 2024-12-19 18:33:12.078917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd498c527704'
down_revision: Union[str, None] = 'ebfdf80d2ddb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN command_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
