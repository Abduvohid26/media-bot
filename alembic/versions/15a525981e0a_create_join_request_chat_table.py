"""create join request chat table

Revision ID: 15a525981e0a
Revises: eb9276c43fdc
Create Date: 2024-05-18 20:35:47.717750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15a525981e0a'
down_revision: Union[str, None] = 'eb9276c43fdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "join_request_chat" (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "chat" VARCHAR(255) NOT NULL,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE join_request_chat;")
