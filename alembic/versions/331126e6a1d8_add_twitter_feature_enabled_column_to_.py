"""add_twitter_feature_enabled_column_to_instance_table

Revision ID: 331126e6a1d8
Revises: 316ce5460606
Create Date: 2025-03-15 14:48:44.892649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '331126e6a1d8'
down_revision: Union[str, None] = '316ce5460606'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN twitter_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
