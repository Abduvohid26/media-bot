"""create referral click table

Revision ID: e5976285c638
Revises: 906f8dcce9ca
Create Date: 2024-04-21 17:04:44.049425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5976285c638'
down_revision: Union[str, None] = '906f8dcce9ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "referral_click" (
      "id" SERIAL PRIMARY KEY,
      "referral_origin" BIGINT REFERENCES "referral" ("id") ON DELETE CASCADE,
      "account_origin" BIGINT REFERENCES "account" ("id") ON DELETE CASCADE,
      "instance_origin" BIGINT REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)


def downgrade() -> None:
  op.execute("DROP TABLE referral_click")
