"""create group table

Revision ID: 451d2236aa48
Revises: 9036f72e2051
Create Date: 2024-07-27 20:55:12.896919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '451d2236aa48'
down_revision: Union[str, None] = '9036f72e2051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "group" (
      "id" SERIAL PRIMARY KEY,
      "group_id" INTEGER NOT NULL,
      "instance_origin" INTEGER REFERENCES "instance"("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      "deleted_at" TIMESTAMP
    );
  """)


def downgrade() -> None:
    pass
