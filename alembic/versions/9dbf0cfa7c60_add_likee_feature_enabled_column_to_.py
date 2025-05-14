"""add_likee_feature_enabled_column_to_instance_table

Revision ID: 9dbf0cfa7c60
Revises: 331126e6a1d8
Create Date: 2025-03-21 13:33:06.473189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dbf0cfa7c60'
down_revision: Union[str, None] = '331126e6a1d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN likee_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
    pass
