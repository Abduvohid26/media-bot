"""create message seen table

Revision ID: 0ef3f9b08017
Revises: 91a1127cd9b7
Create Date: 2024-07-15 21:34:59.039339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ef3f9b08017'
down_revision: Union[str, None] = '91a1127cd9b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE message_seen (
      "id" SERIAL PRIMARY KEY NOT NULL,
      "message_origin" INTEGER REFERENCES "message" ("id") ON DELETE CASCADE,
      "account_origin" INTEGER REFERENCES "account" ("id") ON DELETE CASCADE,
      "instance_origin" INTEGER REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  """)


def downgrade() -> None:
    pass
