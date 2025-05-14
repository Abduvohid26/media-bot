"""add tiktok quota tiktok used to instance quota table

Revision ID: 9e136929bdd1
Revises: 3b42de68e40b
Create Date: 2024-06-03 21:36:43.240488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e136929bdd1'
down_revision: Union[str, None] = '3b42de68e40b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    ALTER TABLE "instance_quota"
      ADD COLUMN "tiktok_quota" BIGINT DEFAULT -1,
      ADD COLUMN "tiktok_used" BIGINT DEFAULT 0
  """)


def downgrade() -> None:
  pass
