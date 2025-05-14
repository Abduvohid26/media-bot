"""add_facebook_feature_enabled_column_to_instance_table

Revision ID: 1e813e2f3741
Revises: 1dc24c476c0d
Create Date: 2025-03-26 15:12:11.123283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e813e2f3741'
down_revision: Union[str, None] = '1dc24c476c0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN facebook_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
