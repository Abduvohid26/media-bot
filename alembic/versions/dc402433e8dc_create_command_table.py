"""create command table

Revision ID: dc402433e8dc
Revises: 47491a5da49a
Create Date: 2024-03-16 10:32:26.748432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc402433e8dc'
down_revision: Union[str, None] = '47491a5da49a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "command" (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "command" VARCHAR(255) NOT NULL,
      "is_enabled" BOOL DEFAULT FALSE,
      "instance_origin" INTEGER REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)

  op.execute("CREATE INDEX IF NOT EXISTS index_command_id ON command(id);")
  op.execute("CREATE INDEX IF NOT EXISTS index_command_command ON command(command);")


def downgrade() -> None:
  op.execute("DROP INDEX index_command;")
  op.execute("DROP INDEX index_command_command;")
  op.execute("DROP TABLE command;")
