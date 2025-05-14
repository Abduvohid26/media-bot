"""create advertisement table

Revision ID: 5b0a6dfc720b
Revises: 3d49154d17b9
Create Date: 2024-05-21 14:57:20.064814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b0a6dfc720b'
down_revision: Union[str, None] = '3d49154d17b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "advertisement" (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "name" VARCHAR(255) NOT NULL,
      "kind" SMALLINT NOT NULL,
      "is_enabled" BOOL DEFAULT FALSE,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE advertisement;")
