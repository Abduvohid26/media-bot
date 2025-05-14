"""rename recognize_from_voice_feature_enabled column to track_recognize_from_voice_feature_enabled

Revision ID: 50971ccc5bde
Revises: 5b6cd9fac734
Create Date: 2024-11-09 04:42:55.847841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50971ccc5bde'
down_revision: Union[str, None] = '5b6cd9fac734'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance RENAME COLUMN recognize_from_voice_feature_enabled TO track_recognize_from_voice_feature_enabled;")


def downgrade() -> None:
  pass
