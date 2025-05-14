"""add instagram_recognize_track_feature_enabled column to instance table

Revision ID: 4d4923e90530
Revises: 9a2b9a3f4c93
Create Date: 2024-11-17 14:40:17.839147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d4923e90530'
down_revision: Union[str, None] = '9a2b9a3f4c93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN instagram_recognize_track_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
