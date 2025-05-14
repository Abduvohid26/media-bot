"""create config table

Revision ID: 399ee62f8d4b
Revises: eca7a446cc90
Create Date: 2024-07-28 08:35:54.743272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '399ee62f8d4b'
down_revision: Union[str, None] = 'eca7a446cc90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "config" (
      "config" VARCHAR(255) PRIMARY KEY NOT NULL,
      "value" TEXT
    );
  """)


def downgrade() -> None:
    pass
