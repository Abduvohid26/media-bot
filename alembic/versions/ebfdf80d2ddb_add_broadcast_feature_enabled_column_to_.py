"""add broadcast_feature_enabled column to instance table

Revision ID: ebfdf80d2ddb
Revises: 326650e8caf2
Create Date: 2024-12-19 18:29:58.798974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebfdf80d2ddb'
down_revision: Union[str, None] = '326650e8caf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN broadcast_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
