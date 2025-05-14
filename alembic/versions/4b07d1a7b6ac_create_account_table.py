"""create account table

Revision ID: 4b07d1a7b6ac
Revises: ee608188e44d
Create Date: 2024-03-23 14:49:25.838162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b07d1a7b6ac'
down_revision: Union[str, None] = 'ee608188e44d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
  op.execute("""
    CREATE TABLE "account" (
      "id" SERIAL PRIMARY KEY,
      "telegram_id" BIGINT NOT NULL,
      "language_origin" INTEGER REFERENCES "language" ("id") ON DELETE SET NULL,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id"),
      "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE("telegram_id", "instance_origin")
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE account;")
