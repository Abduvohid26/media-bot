"""add recognize_from_voice_feature_enabled column to instance table

Revision ID: e7c0f84e69af
Revises: 4d85efca83a0
Create Date: 2024-10-20 12:57:35.324938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7c0f84e69af'
down_revision: Union[str, None] = '4d85efca83a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN recognize_from_voice_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
