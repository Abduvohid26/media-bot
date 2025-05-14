"""create required join mark table

Revision ID: 4c2ff3256c7d
Revises: 0e349732c424
Create Date: 2024-04-27 18:12:49.315075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2ff3256c7d'
down_revision: Union[str, None] = '0e349732c424'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "required_join_mark" (
      "id" SERIAL PRIMARY KEY,
      "required_join_origin" INTEGER REFERENCES "required_join" ("id") ON DELETE CASCADE,
      "account_origin" INTEGER REFERENCES "account" ("id") ON DELETE CASCADE,
      "instance_origin" INTEGER REFERENCES "instance" ("id") ON DELETE CASCADE,
      "has_joined" BOOL DEFAULT FALSE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE required_join_mark")
