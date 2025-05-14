"""add youtube_search feature enabled column to instance table

Revision ID: 533fa446df56
Revises: c797650514cd
Create Date: 2025-03-02 16:30:41.890169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '533fa446df56'
down_revision: Union[str, None] = 'c797650514cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE INSTANCE ADD COLUMN youtube_search_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
