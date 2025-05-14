"""create instance quota table

Revision ID: be8c4f6336ef
Revises: 5de691832b16
Create Date: 2024-06-02 09:26:09.090162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be8c4f6336ef'
down_revision: Union[str, None] = '5de691832b16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "instance_quota" (
      "id" SERIAL PRIMARY KEY,
      "track_search_quota" BIGINT DEFAULT -1,
      "track_download_quota" BIGINT DEFAULT -1,
      "track_search_used" BIGINT DEFAULT 0,
      "track_download_used" BIGINT DEFAULT 0,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE
    );
  """)


def downgrade() -> None:
    pass
