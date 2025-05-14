"""add track_recognize_from_video_note_feature_enabled column to instance table

Revision ID: 9a2b9a3f4c93
Revises: 50971ccc5bde
Create Date: 2024-11-09 13:13:49.533299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a2b9a3f4c93'
down_revision: Union[str, None] = '50971ccc5bde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_recognize_from_video_note_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
