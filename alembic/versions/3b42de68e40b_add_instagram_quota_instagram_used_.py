"""add instagram quota instagram used columns to instance quota table

Revision ID: 3b42de68e40b
Revises: 966f40c72e69
Create Date: 2024-06-02 21:14:55.063226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b42de68e40b'
down_revision: Union[str, None] = '966f40c72e69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    ALTER TABLE "instance_quota"
      ADD COLUMN "instagram_quota" BIGINT DEFAULT -1,
      ADD COLUMN "instagram_used" BIGINT DEFAULT 0
  """)


def downgrade() -> None:
  pass
