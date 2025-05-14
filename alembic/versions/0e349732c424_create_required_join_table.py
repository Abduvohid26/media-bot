"""create required join table

Revision ID: 0e349732c424
Revises: 74ac3dc57a7f
Create Date: 2024-04-26 14:56:50.643046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e349732c424'
down_revision: Union[str, None] = '74ac3dc57a7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "required_join" (
      "id" SERIAL PRIMARY KEY,
      "kind" SMALLINT NOT NULL,
      "target_chat" VARCHAR NOT NULL,
      "join_link" VARCHAR DEFAULT NULL,
      "is_optional" BOOL DEFAULT FALSE,
      "is_enabled" BOOL DEFAULT FALSE,
      "target_join_count" BIGINT DEFAULT 0,
      "target_end_time" TIMESTAMP DEFAULT NULL,
      "language_origin" INTEGER REFERENCES "language" ("id") ON DELETE SET NULL,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE required_join")
