"""add youtube_feature_enabled column to instance table

Revision ID: 534ecf196ddc
Revises: 4d4923e90530
Create Date: 2024-11-23 03:30:29.175554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '534ecf196ddc'
down_revision: Union[str, None] = '4d4923e90530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN youtube_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
