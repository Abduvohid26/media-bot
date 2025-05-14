"""add cursor column to join_request_chat table

Revision ID: 407fd3957a09
Revises: 9ac3730c873b
Create Date: 2024-12-16 17:54:15.830979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '407fd3957a09'
down_revision: Union[str, None] = '9ac3730c873b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE join_request_chat ADD COLUMN cursor BIGINT DEFAULT 0;")


def downgrade() -> None:
  pass
