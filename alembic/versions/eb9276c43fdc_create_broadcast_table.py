"""create broadcast table

Revision ID: eb9276c43fdc
Revises: 8cd8d6475807
Create Date: 2024-05-13 14:01:52.781078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb9276c43fdc'
down_revision: Union[str, None] = '8cd8d6475807'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "broadcast" (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "name" VARCHAR(255) NOT NULL,
      "status" SMALLINT DEFAULT 0,
      "is_group" BOOL DEFAULT FALSE,
      "is_silent" BOOL DEFAULT FALSE,
      "mps" INTEGER DEFAULT 0,
      "jobs" INTEGER DEFAULT NULL,
      "cursor" INTEGER DEFAULT 0,
      "eta" INTEGER DEFAULT 0,
      "succeeded_jobs" INTEGER DEFAULT 0,
      "failed_jobs" INTEGER DEFAULT 0,
      "blocked_jobs" INTEGER DEFAULT 0,
      "message_origin" INTEGER REFERENCES "message" ("id") ON DELETE CASCADE NOT NULL,
      "instance_origin" INTEGER REFERENCES "instance" ("id") ON DELETE CASCADE NOT NULL,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE broadcast")
