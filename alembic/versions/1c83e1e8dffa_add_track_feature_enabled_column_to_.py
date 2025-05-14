"""add track_feature_enabled column to instance table

Revision ID: 1c83e1e8dffa
Revises: 407fd3957a09
Create Date: 2024-12-19 17:51:16.787984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c83e1e8dffa'
down_revision: Union[str, None] = '407fd3957a09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
