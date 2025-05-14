"""add join request feature enabled column to instance table

Revision ID: 89ccc581f294
Revises: cb8cfebb52f1
Create Date: 2024-07-23 08:20:16.173987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89ccc581f294'
down_revision: Union[str, None] = 'cb8cfebb52f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN join_request_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
