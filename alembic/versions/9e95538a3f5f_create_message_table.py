"""create message table

Revision ID: 9e95538a3f5f
Revises: dc402433e8dc
Create Date: 2024-03-16 22:17:51.084434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e95538a3f5f'
down_revision: Union[str, None] = 'dc402433e8dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "message" (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "message" JSONB NOT NULL,
      "command_origin" INTEGER REFERENCES "command" ("id") ON DELETE CASCADE,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "language_origin" INTEGER REFERENCES "language" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
  """)
  op.execute("CREATE INDEX IF NOT EXISTS index_message_id ON message(id);")


def downgrade() -> None:
  op.execute("DROP INDEX index_message_id;")
  op.execute("DROP TABLE message;")