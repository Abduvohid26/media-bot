"""create account table

Revision ID: 47491a5da49a
Revises: c4c2973d8cf1
Create Date: 2024-03-14 22:02:52.158701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47491a5da49a'
down_revision: Union[str, None] = 'c4c2973d8cf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "account" (
      "id" SERIAL PRIMARY KEY,
      "language_origin" INTEGER REFERENCES "language" ("id") ON DELETE SET NULL,
      "instance_origin" INTEGER REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)

def downgrade() -> None:
  op.execute("DROP TABLE account;")
