"""add video search quota video download quota video search used video download used columns to instance quota table

Revision ID: 966f40c72e69
Revises: be8c4f6336ef
Create Date: 2024-06-02 19:50:13.132316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '966f40c72e69'
down_revision: Union[str, None] = 'be8c4f6336ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    ALTER TABLE "instance_quota"
      ADD COLUMN "video_search_quota" BIGINT DEFAULT -1,
      ADD COLUMN "video_download_quota" BIGINT DEFAULT -1,
      ADD COLUMN "video_search_used" BIGINT DEFAULT 0,
      ADD COLUMN "video_download_used" BIGINT DEFAULT 0;
  """)


def downgrade() -> None:
  pass
