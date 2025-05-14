"""add_tumblr_feature_enabled_column_to_instance_table

Revision ID: 3296e1fe374d
Revises: 9dbf0cfa7c60
Create Date: 2025-03-21 14:50:20.160799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3296e1fe374d'
down_revision: Union[str, None] = '9dbf0cfa7c60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN tumblr_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
