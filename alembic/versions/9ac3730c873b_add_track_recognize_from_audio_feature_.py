"""add track_recognize_from_audio_feature_enabled column to instance

Revision ID: 9ac3730c873b
Revises: 263870ebe30a
Create Date: 2024-11-25 17:35:51.683148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ac3730c873b'
down_revision: Union[str, None] = '263870ebe30a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_recognize_from_audio_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
