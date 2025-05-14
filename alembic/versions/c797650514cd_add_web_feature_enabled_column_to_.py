"""add web_feature_enabled column to instance table

Revision ID: c797650514cd
Revises: 4041d8bb6aa2
Create Date: 2024-12-20 04:33:34.708919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c797650514cd'
down_revision: Union[str, None] = '4041d8bb6aa2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN web_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
  pass
