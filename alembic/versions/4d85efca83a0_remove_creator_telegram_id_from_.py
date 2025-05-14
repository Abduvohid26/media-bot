"""remove creator telegram id from instance table

Revision ID: 4d85efca83a0
Revises: 74c57110e19e
Create Date: 2024-09-05 10:58:33.541472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d85efca83a0'
down_revision: Union[str, None] = '74c57110e19e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN creator_telegram_id;")


def downgrade() -> None:
  pass
