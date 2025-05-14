"""add_pinterest_feature_enabled_column_to_instance_table

Revision ID: 1dc24c476c0d
Revises: 3296e1fe374d
Create Date: 2025-03-22 14:48:26.221350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dc24c476c0d'
down_revision: Union[str, None] = '3296e1fe374d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN pinterest_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
