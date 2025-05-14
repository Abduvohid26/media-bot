"""add tiktok_recognize_track_feature_enabled column to instance table

Revision ID: 263870ebe30a
Revises: 48c49633b584
Create Date: 2024-11-24 07:45:40.931220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '263870ebe30a'
down_revision: Union[str, None] = '48c49633b584'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN tiktok_recognize_track_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
